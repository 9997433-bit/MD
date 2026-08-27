using System;

namespace Aetherboard.VR
{
    /// <summary>
    /// Pluggable client transport — foundation for swapping TCP / WebSocket / future Netcode.
    /// </summary>
    public interface IBattleNetTransport : IDisposable
    {
        string Name { get; }
        bool IsConnected { get; }
        bool Connect(string host, int port, int timeoutMs = 3000);
        void Disconnect();
        bool Send(string text, bool lineDelimited);
        void StartReceiveLoop(Func<string, bool> onMessage);
    }

    public enum BattleNetTransportKind
    {
        Tcp,
        WebSocket
    }

    public static class BattleNetTransportFactory
    {
        public static IBattleNetTransport Create(BattleNetTransportKind kind) => kind switch
        {
            BattleNetTransportKind.WebSocket => new BattleWebSocketNetTransport(),
            _ => new BattleTcpNetTransport()
        };
    }
}
