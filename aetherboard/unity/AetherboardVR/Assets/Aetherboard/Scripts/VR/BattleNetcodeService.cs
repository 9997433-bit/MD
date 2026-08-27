using System;
using UnityEngine;
using Aetherboard.Core;
using Aetherboard.NetcodeIntegration;

namespace Aetherboard.VR
{
    /// <summary>
    /// NGO integration hook — registers battle sync handlers when Netcode is present.
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

        private void OnEnable()
        {
            BattleNetcodeHostCoordinator.OnRemoteBattleMessage += ReceiveBattleMessage;
        }

        private void OnDisable()
        {
            BattleNetcodeHostCoordinator.OnRemoteBattleMessage -= ReceiveBattleMessage;
        }

        private void OnDestroy()
        {
            if (_instance == this) _instance = null;
        }

        public void PublishBattleMessage(string json)
        {
            if (string.IsNullOrEmpty(json)) return;
            OnBattleMessage?.Invoke(json);
        }

        public void ReceiveBattleMessage(string json) => OnBattleMessage?.Invoke(json);

        private void TryRegisterNetcodeHandlers()
        {
            BattleNetcodeRuntime.LogStatus();
            NetcodeReady = BattleNetcodeRuntime.IsAvailable;
            if (!NetcodeReady) return;
            Debug.Log("[Aetherboard] BattleNetcodeService ready — NGO CustomMessaging via BattleNetcodeFacade");
        }

        public static byte[] FrameForNetcode(string json) => BattleNetMessageCodec.Frame(json);

        public static string UnframeFromNetcode(byte[] data, int length) =>
            BattleNetMessageCodec.Unframe(data, length);
    }
}
