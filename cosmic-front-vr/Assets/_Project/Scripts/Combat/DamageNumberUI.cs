using UnityEngine;

namespace CosmicFront.Combat
{
    /// <summary>
    /// Optional world-space floating damage number (TextMesh).
    /// </summary>
    public class DamageNumberUI : MonoBehaviour
    {
        private const float Lifetime = 0.75f;
        private const float RiseSpeed = 1.2f;

        private float _remaining;
        private TextMesh _text;

        public static void Spawn(Vector3 worldPosition, float amount)
        {
            var go = new GameObject("DamageNumber");
            go.transform.position = worldPosition + Vector3.up * 0.4f;

            var text = go.AddComponent<TextMesh>();
            text.text = Mathf.Max(1, Mathf.RoundToInt(amount)).ToString();
            text.fontSize = 64;
            text.characterSize = 0.04f;
            text.anchor = TextAnchor.MiddleCenter;
            text.alignment = TextAlignment.Center;
            text.color = new Color(1f, 0.35f, 0.2f);

            var ui = go.AddComponent<DamageNumberUI>();
            ui._text = text;
            ui._remaining = Lifetime;
        }

        private void Update()
        {
            _remaining -= Time.deltaTime;
            transform.position += Vector3.up * (RiseSpeed * Time.deltaTime);

            var cam = Camera.main;
            if (cam != null)
            {
                transform.rotation = Quaternion.LookRotation(transform.position - cam.transform.position);
            }

            if (_text != null)
            {
                var c = _text.color;
                c.a = Mathf.Clamp01(_remaining / Lifetime);
                _text.color = c;
            }

            if (_remaining <= 0f)
            {
                Destroy(gameObject);
            }
        }
    }
}
