using UnityEngine;
using UnityEngine.UI;
using CosmicFront.Core;
using CosmicFront.Modes;

namespace CosmicFront.UI
{
    /// <summary>
    /// World-space label above a capture point: name + ownership.
    /// </summary>
    [RequireComponent(typeof(CapturePoint))]
    public class CapturePointWorldLabel : MonoBehaviour
    {
        [SerializeField] private Text label;
        [SerializeField] private Vector3 worldOffset = new Vector3(0f, 2.4f, 0f);
        [SerializeField] private float canvasScale = 0.025f;

        private CapturePoint _point;
        private Transform _canvasTransform;
        private TeamId _lastOwner = (TeamId)(-1);
        private string _lastName;

        private void Awake()
        {
            _point = GetComponent<CapturePoint>();
            EnsureLabel();
            RefreshText(force: true);
        }

        private void LateUpdate()
        {
            if (_point == null || label == null) return;

            if (_canvasTransform != null)
            {
                _canvasTransform.position = transform.position + worldOffset;
                var cam = Camera.main;
                if (cam != null)
                {
                    var toCam = _canvasTransform.position - cam.transform.position;
                    if (toCam.sqrMagnitude > 0.001f)
                    {
                        _canvasTransform.rotation = Quaternion.LookRotation(toCam);
                    }
                }
            }

            RefreshText(force: false);
        }

        private void RefreshText(bool force)
        {
            var owner = _point.Owner;
            var name = _point.PointName;
            if (!force && owner == _lastOwner && name == _lastName) return;

            _lastOwner = owner;
            _lastName = name;
            label.text = $"{name} — {OwnerLabel(owner)}";
            label.color = CapturePointVisual.ColorFor(owner);
        }

        private void EnsureLabel()
        {
            if (label != null)
            {
                _canvasTransform = label.canvas != null ? label.canvas.transform : null;
                return;
            }

            var canvasGo = new GameObject("CapturePointLabelCanvas");
            _canvasTransform = canvasGo.transform;
            _canvasTransform.SetParent(transform, false);
            _canvasTransform.localPosition = worldOffset;
            _canvasTransform.localScale = Vector3.one * canvasScale;

            var canvas = canvasGo.AddComponent<Canvas>();
            canvas.renderMode = RenderMode.WorldSpace;
            var rt = canvasGo.GetComponent<RectTransform>();
            rt.sizeDelta = new Vector2(280f, 48f);

            var textGo = new GameObject("Label");
            textGo.transform.SetParent(canvasGo.transform, false);
            label = textGo.AddComponent<Text>();
            label.font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
            label.fontSize = 32;
            label.alignment = TextAnchor.MiddleCenter;
            label.horizontalOverflow = HorizontalWrapMode.Overflow;
            label.verticalOverflow = VerticalWrapMode.Overflow;
            label.color = Color.white;
            label.raycastTarget = false;

            var textRt = label.rectTransform;
            textRt.anchorMin = Vector2.zero;
            textRt.anchorMax = Vector2.one;
            textRt.offsetMin = Vector2.zero;
            textRt.offsetMax = Vector2.zero;
        }

        private static string OwnerLabel(TeamId owner)
        {
            switch (owner)
            {
                case TeamId.Terran: return "地球联合";
                case TeamId.Orbital: return "轨道联盟";
                default: return "中立";
            }
        }
    }
}
