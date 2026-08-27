using System;
using UnityEngine;
using Aetherboard.Core;

namespace Aetherboard.VR
{
    /// <summary>
    /// NGO integration hook — registers battle sync handlers when Netcode is present.
    /// Falls back to no-op; actual client IO remains IBattleNetTransport until NGO transport lands.
    /// </summary>
    public class BattleNetcodeService : MonoBehaviour
    {
        public const string BattleMessageName = "AetherboardBattleSync";

        public event Action<string> OnBattleMessage;

        private static BattleNetcodeService _instance;

        public static BattleNetcodeService Instance => _instance;

        public bool NetcodeReady { get; private set; }

        private void Awake()
        {
            if (_instance != null && _instance != this)
            {
                Destroy(gameObject);
                return;
            }
            _instance = this;
            DontDestroyOnLoad(gameObject);
            TryRegisterNetcodeHandlers();
        }

        private void OnDestroy()
        {
            if (_instance == this) _instance = null;
        }

        public void PublishBattleMessage(string json)
        {
            if (string.IsNullOrEmpty(json)) return;
            OnBattleMessage?.Invoke(json);
            if (!NetcodeReady) return;
            // Future: CustomMessagingManager.SendNamedMessage(BattleMessageName, Frame(json), ...)
        }

        public void ReceiveBattleMessage(string json) => OnBattleMessage?.Invoke(json);

        private void TryRegisterNetcodeHandlers()
        {
            BattleNetcodeRuntime.LogStatus();
            NetcodeReady = BattleNetcodeRuntime.IsAvailable;
            if (!NetcodeReady) return;
            Debug.Log("[Aetherboard] BattleNetcodeService ready — wire CustomMessagingManager when NGO host starts");
        }

        public static byte[] FrameForNetcode(string json) => BattleNetMessageCodec.Frame(json);

        public static string UnframeFromNetcode(byte[] data, int length) =>
            BattleNetMessageCodec.Unframe(data, length);
    }
}
