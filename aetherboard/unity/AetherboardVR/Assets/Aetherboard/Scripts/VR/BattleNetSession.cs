using UnityEngine;
using Aetherboard.Core;

namespace Aetherboard.VR
{
    /// <summary>
    /// Local host/client stub — exchanges JSON snapshots until real networking is added.
    /// </summary>
    public class BattleNetSession : MonoBehaviour
    {
        [SerializeField] private BattleDirector director;

        private string _hostSnapshot;

        private void Awake()
        {
            if (director == null) director = GetComponent<BattleDirector>();
        }

        public string HostPublishState()
        {
            if (director == null) return null;
            _hostSnapshot = director.ExportSnapshotJson();
            return _hostSnapshot;
        }

        public bool ClientApplyState(string json)
        {
            if (director == null) return false;
            return director.ImportSnapshotJson(json);
        }

        public string GetLastHostSnapshot() => _hostSnapshot;

        public string ExportCommandLog() => director?.CommandLog.ToJson();
    }
}
