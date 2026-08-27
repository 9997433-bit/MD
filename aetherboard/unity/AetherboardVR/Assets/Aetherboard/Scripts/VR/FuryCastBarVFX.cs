using UnityEngine;
using Aetherboard.Core;

namespace Aetherboard.VR
{
    /// <summary>
    /// Boss fury / cyclone cast bar floating above hologram.
    /// </summary>
    public class FuryCastBarVFX : MonoBehaviour
    {
        private Transform _barRoot;
        private Transform _fill;
        private BossState _boss;
        private float _pulse;

        public void Initialize(Transform parent)
        {
            _barRoot = new GameObject("FuryCastBar").transform;
            _barRoot.SetParent(parent, false);
            _barRoot.localPosition = new Vector3(0, 0.28f, 0);

            var bg = GameObject.CreatePrimitive(PrimitiveType.Cube);
            bg.name = "BarBG";
            bg.transform.SetParent(_barRoot, false);
            bg.transform.localScale = new Vector3(0.35f, 0.025f, 0.04f);
            bg.GetComponent<Renderer>().material =
                ProceduralAssets.CreateUnlitMaterial(new Color(0.15f, 0.15f, 0.15f));
            Destroy(bg.GetComponent<Collider>());

            var fillGo = GameObject.CreatePrimitive(PrimitiveType.Cube);
            fillGo.name = "BarFill";
            fillGo.transform.SetParent(_barRoot, false);
            fillGo.transform.localScale = new Vector3(0.34f, 0.03f, 0.035f);
            _fill = fillGo.transform;
            _fill.GetComponent<Renderer>().material =
                ProceduralAssets.CreateUnlitMaterial(new Color(0.95f, 0.15f, 0.1f));
            Destroy(fillGo.GetComponent<Collider>());

            _barRoot.gameObject.SetActive(false);
        }

        public void Bind(BossState boss)
        {
            _boss = boss;
            var casting = boss.FuryCastTurns > 0;
            _barRoot.gameObject.SetActive(casting);
            if (!casting) return;

            var ratio = boss.FuryCastTurns / 2f;
            _fill.localScale = new Vector3(0.34f * ratio, 0.03f, 0.035f);
            _fill.localPosition = new Vector3(-0.17f * (1f - ratio), 0, -0.001f);

            _pulse += Time.deltaTime * 4f;
            var c = new Color(0.95f, 0.15f + Mathf.Sin(_pulse) * 0.15f, 0.1f);
            _fill.GetComponent<Renderer>().material.color = c;
        }
    }
}
