using System;
using System.Collections.Generic;
using System.Threading;
using Aetherboard.NetcodeIntegration;

namespace Aetherboard.VR
{
    /// <summary>
    /// Native NGO client transport — UnityTransport + CustomMessaging (no WebSocket relay).
    /// </summary>
    public sealed class BattleNetcodeNativeTransport : IBattleNetTransport
    {
        private readonly object _lock = new();
        private readonly Queue<string> _queue = new();
        private bool _subscribed;

        public string Name => BattleNetcodeRuntime.IsAvailable ? "Netcode-Native" : "Netcode-Native (NGO missing)";
        public bool IsConnected => BattleNetcodeNativeBridge.IsConnected;

        public bool Connect(string host, int port, int timeoutMs = 3000)
        {
            BattleNetcodeRuntime.LogStatus();
            if (!BattleNetcodeRuntime.IsAvailable)
            {
                UnityEngine.Debug.LogWarning("[Aetherboard] Unity Netcode not installed — cannot use native transport.");
                return false;
            }

            Subscribe();
            return BattleNetcodeNativeBridge.ConnectClient(host, port, timeoutMs);
        }

        public void Disconnect()
        {
            Unsubscribe();
            BattleNetcodeNativeBridge.Shutdown();
            lock (_lock) _queue.Clear();
        }

        public void Dispose() => Disconnect();

        public bool Send(string text, bool lineDelimited) =>
            BattleNetcodeNativeBridge.SendCommand(text);

        public void StartReceiveLoop(Func<string, bool> onMessage)
        {
            while (IsConnected)
            {
                string line = null;
                lock (_lock)
                {
                    if (_queue.Count > 0) line = _queue.Dequeue();
                }

                if (line != null)
                {
                    if (!onMessage(line)) break;
                }
                else
                {
                    Thread.Sleep(10);
                }
            }
        }

        private void Subscribe()
        {
            if (_subscribed) return;
            BattleNetcodeHostCoordinator.OnRemoteBattleMessage += EnqueueLine;
            _subscribed = true;
        }

        private void Unsubscribe()
        {
            if (!_subscribed) return;
            BattleNetcodeHostCoordinator.OnRemoteBattleMessage -= EnqueueLine;
            _subscribed = false;
        }

        private void EnqueueLine(string line)
        {
            if (string.IsNullOrEmpty(line)) return;
            lock (_lock) _queue.Enqueue(line);
        }
    }
}
