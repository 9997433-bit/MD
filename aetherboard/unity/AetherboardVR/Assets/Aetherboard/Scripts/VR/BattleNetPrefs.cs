using UnityEngine;

namespace Aetherboard.VR
{
    /// <summary>
    /// Persists battle network settings across sessions (Quest / Editor).
    /// </summary>
    public static class BattleNetPrefs
    {
        private const string HostKey = "aetherboard.net.host";
        private const string TransportKey = "aetherboard.net.transport";
        private const string PlayerIdKey = "aetherboard.net.playerId";

        public static string LoadHost(string fallback = "127.0.0.1") =>
            PlayerPrefs.GetString(HostKey, fallback);

        public static void SaveHost(string host)
        {
            if (string.IsNullOrWhiteSpace(host)) return;
            PlayerPrefs.SetString(HostKey, host.Trim());
            PlayerPrefs.Save();
        }

        public static NetClientTransport LoadTransport(NetClientTransport fallback = NetClientTransport.Auto)
        {
            if (!PlayerPrefs.HasKey(TransportKey)) return fallback;
            var raw = PlayerPrefs.GetInt(TransportKey, (int)fallback);
            return System.Enum.IsDefined(typeof(NetClientTransport), raw)
                ? (NetClientTransport)raw
                : fallback;
        }

        public static void SaveTransport(NetClientTransport transport)
        {
            PlayerPrefs.SetInt(TransportKey, (int)transport);
            PlayerPrefs.Save();
        }

        public static int LoadPlayerId(int fallback = 1)
        {
            var id = PlayerPrefs.GetInt(PlayerIdKey, fallback);
            return id == 2 ? 2 : 1;
        }

        public static void SavePlayerId(int playerId)
        {
            PlayerPrefs.SetInt(PlayerIdKey, playerId == 2 ? 2 : 1);
            PlayerPrefs.Save();
        }

        public static void ApplyTo(BattleNetSession session)
        {
            if (session == null) return;
            session.SetHostAddress(LoadHost(session.HostAddress));
            session.SetClientTransport(LoadTransport(session.ClientTransport));
            session.SetLocalPlayerId(LoadPlayerId(session.LocalPlayerId));
        }

        public static void SaveFrom(BattleNetSession session)
        {
            if (session == null) return;
            SaveHost(session.HostAddress);
            SaveTransport(session.ClientTransport);
            SavePlayerId(session.LocalPlayerId);
        }
    }
}
