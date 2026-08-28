"""Tests for the dry-run USB command-plane replay builder."""
from __future__ import annotations

import json

from scripts import replay_usb_command_plane as replay


def test_protocol_log_entries_are_ordered_and_include_expected_in(tmp_path):
    protocol_log = tmp_path / "protocol_log.json"
    protocol_log.write_text(
        json.dumps(
            {
                "commands": [
                    {
                        "seq": 7,
                        "direction": "host_to_device",
                        "endpoint": "0x01 -> 0x81",
                        "request_hex": "00:01",
                        "response_hex": "aabbcc",
                    },
                    {
                        "seq": 8,
                        "direction": "device_to_host",
                        "endpoint": "0x81",
                        "request_hex": "ffff",
                    },
                    {
                        "seq": 9,
                        "direction": "host_to_device",
                        "endpoint": "0x01",
                        "request_hex": "0203",
                        "response_hex": "",
                    },
                ]
            }
        ),
        encoding="utf-8",
    )

    entries = replay.entries_from_protocol_log(protocol_log)

    assert entries == [
        {
            "seq": 0,
            "out_hex": "0001",
            "source_command_seq": 7,
            "expected_in_length": 3,
            "expected_in_hex": "aabbcc",
        },
        {"seq": 1, "out_hex": "0203", "source_command_seq": 9},
    ]


def test_pcap_entries_pair_next_in_before_another_out(tmp_path, monkeypatch):
    pcap = tmp_path / "usb_session.pcapng"
    pcap.write_bytes(b"pcap fixture placeholder")
    monkeypatch.setattr(replay, "_find_primary_address", lambda _: 24)
    monkeypatch.setattr(
        replay,
        "_run_tshark",
        lambda *_: [
            ["10", "1.000", "0x01", "0001"],
            ["11", "1.125", "0x81", "aabb"],
            ["12", "2.000", "0x01", "0203"],
        ],
    )

    entries = replay.entries_from_pcap(pcap)

    assert entries[0]["out_hex"] == "0001"
    assert entries[0]["expected_in_length"] == 2
    assert entries[0]["expected_in_hex"] == "aabb"
    assert entries[0]["response_delay_seconds"] == 0.125
    assert entries[1]["out_hex"] == "0203"
    assert "expected_in_hex" not in entries[1]


def test_live_flag_builds_manifest_then_refuses_replay(tmp_path, capsys):
    protocol_log = tmp_path / "protocol_log.json"
    output = tmp_path / "replay.json"
    protocol_log.write_text(
        json.dumps(
            {
                "commands": [
                    {
                        "seq": 0,
                        "direction": "host_to_device",
                        "endpoint": "0x01",
                        "request_hex": "0102",
                        "response_hex": "03",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    status = replay.main(
        [
            "--source",
            "protocol_log",
            "--protocol-log",
            str(protocol_log),
            "--output",
            str(output),
            "--live",
        ]
    )

    assert status == 2
    assert output.exists()
    assert json.loads(output.read_text(encoding="utf-8"))["entry_count"] == 1
    assert "no USB data was sent" in capsys.readouterr().err
