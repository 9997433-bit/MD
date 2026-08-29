using UnityEngine;
using CosmicFront.Core;
using CosmicFront.Modes;

namespace CosmicFront.Modes
{
    /// <summary>
    /// Progress ring (scaled cylinder) that fills with capture absolute progress.
    /// </summary>
    [RequireComponent(typeof(CapturePoint))]
    public class CapturePointProgressRing : MonoBehaviour
    {
        [SerializeField] private Transform ring;
        [SerializeField] private float minScale = 0.2f;
        [SerializeField] private float maxScale = 1f;

        private CapturePoint _point;
        private Renderer _renderer;

        private void Awake()
        {
            _point = GetComponent<CapturePoint>();
            if (ring == null)
            {
                var go = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
                go.name = "ProgressRing";
                go.transform.SetParent(transform, false);
                go.transform.localPosition = new Vector3(0f, 0.35f, 0f);
                go.transform.localScale = new Vector3(1.1f, 0.05f, 1.1f);
                var col = go.GetComponent<Collider>();
                if (col != null)
                {
                    Destroy(col);
                }

                ring = go.transform;
            }

            _renderer = ring.GetComponent<Renderer>();
        }

        private void LateUpdate()
        {
            if (_point == null || ring == null)
            {
                return;
            }

            var t = Mathf.Abs(_point.CaptureProgress);
            var s = Mathf.Lerp(minScale, maxScale, t);
            ring.localScale = new Vector3(s * 1.1f, 0.05f, s * 1.1f);

            if (_renderer != null)
            {
                var color = _point.Owner switch
                {
                    TeamId.Terran => new Color(0.2f, 0.85f, 0.35f, 0.7f),
                    TeamId.Orbital => new Color(0.7f, 0.35f, 0.9f, 0.7f),
                    TeamId.Neutral => new Color(0.75f, 0.9f, 1f, 0.7f),
                    _ => new Color(0.7f, 0.7f, 0.75f, 0.45f)
                };
                _renderer.material.color = color;
            }
        }
    }
}
