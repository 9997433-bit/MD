using UnityEngine;
using Aetherboard.Core;

namespace Aetherboard.VR
{
    public class BossHologramView : MonoBehaviour
    {
        [SerializeField] private Transform hologramRoot;
        private BossState _last;

        public void InitializeProcedural(Transform parent)
        {
            hologramRoot = new GameObject("BossHologram").transform;
            hologramRoot.SetParent(parent, false);
            hologramRoot.localPosition = new Vector3(0, 0.55f, 0.15f);
            var sphere = GameObject.CreatePrimitive(PrimitiveType.Sphere);
            sphere.transform.SetParent(hologramRoot, false);
            sphere.transform.localScale = Vector3.one * 0.18f;
            var col = sphere.GetComponent<Collider>();
            if (col != null) Destroy(col);
            var r = sphere.GetComponent<Renderer>();
            r.material = ProceduralAssets.CreateUnlitMaterial(new Color(0.9f, 0.25f, 0.2f, 0.75f));
        }

        public void Bind(BossState boss)
        {
            _last = boss;
            if (hologramRoot != null)
            {
                var scale = 0.14f + 0.08f * (boss.Hp / (float)boss.MaxHp);
                hologramRoot.localScale = Vector3.one * scale;
                if (boss.FuryCastTurns > 0)
                    hologramRoot.Rotate(Vector3.up, 90f * Time.deltaTime);
            }
        }

        private void OnGUI()
        {
            if (_last == null) return;
            var rect = new Rect(Screen.width - 220, 12, 200, 80);
            GUI.Box(rect, "");
            GUI.Label(new Rect(rect.x + 8, rect.y + 8, 180, 20), _last.Name);
            GUI.Label(new Rect(rect.x + 8, rect.y + 28, 180, 20),
                $"HP {_last.Hp}/{_last.MaxHp}  P{_last.Phase}");
            if (_last.FuryCastTurns > 0)
                GUI.Label(new Rect(rect.x + 8, rect.y + 48, 180, 20),
                    $"读条: {_last.FuryCastTurns}");
        }
    }
}
