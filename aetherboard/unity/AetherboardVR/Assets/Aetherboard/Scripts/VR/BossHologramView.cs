using UnityEngine;
using Aetherboard.Core;

namespace Aetherboard.VR
{
    /// <summary>
    /// Boss hologram display — 3D labels, themed core, fury cast bar.
    /// </summary>
    public class BossHologramView : MonoBehaviour
    {
        private BossHologramBuilder _builder;
        private FuryCastBarVFX _furyBar;
        private Transform _hologramRoot;

        public void InitializeProcedural(Transform parent)
        {
            var holoGo = new GameObject("BossHologram");
            holoGo.transform.SetParent(parent, false);
            holoGo.transform.localPosition = new Vector3(0, 0.55f, 0.15f);
            _hologramRoot = holoGo.transform;

            _builder = holoGo.AddComponent<BossHologramBuilder>();
            _builder.BuildLocal();

            _furyBar = holoGo.AddComponent<FuryCastBarVFX>();
            _furyBar.Initialize(_hologramRoot);
        }

        private void LateUpdate() => _builder?.Tick(Time.deltaTime);

        public void Bind(BossState boss, string bossId = "earth")
        {
            _builder?.UpdateState(boss, bossId);
            _furyBar?.Bind(boss, bossId);
        }
    }
}
