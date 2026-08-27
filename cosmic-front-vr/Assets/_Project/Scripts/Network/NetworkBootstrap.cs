namespace CosmicFront.Network
{
    /// <summary>
    /// P2 placeholder. Install Photon Fusion or Fish-Net, then implement room flow here.
    /// See docs/NETWORK_PLAN.md
    /// </summary>
    public static class NetworkBootstrap
    {
        public const int MaxPlayers = 16;
        public const string GameVersion = "0.1.0";

        public static bool IsOnlineReady => false;

        public static void CreateRoom(string roomName)
        {
            UnityEngine.Debug.Log($"[NetworkBootstrap] P2 TODO: CreateRoom {roomName}");
        }

        public static void JoinRoom(string roomName)
        {
            UnityEngine.Debug.Log($"[NetworkBootstrap] P2 TODO: JoinRoom {roomName}");
        }
    }
}
