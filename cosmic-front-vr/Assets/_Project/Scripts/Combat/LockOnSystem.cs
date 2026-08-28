using UnityEngine;
using CosmicFront.Core;

namespace CosmicFront.Combat
{
    public class LockOnSystem : MonoBehaviour
    {
        [SerializeField] private float lockConeDegrees = 15f;
        [SerializeField] private float lockRange = 200f;
        [SerializeField] private LayerMask targetLayers = ~0;

        public void ConfigureSensors(float range, float coneDegrees)
        {
            lockRange = range;
            lockConeDegrees = coneDegrees;
        }

        private readonly System.Collections.Generic.List<Transform> _candidates = new System.Collections.Generic.List<Transform>();
        private int _candidateIndex;

        public void UpdateAiming(Transform origin)
        {
            if (origin == null)
            {
                return;
            }

            RefreshCandidates(origin);

            if (CurrentTarget != null && !_candidates.Contains(CurrentTarget))
            {
                CurrentTarget = _candidates.Count > 0 ? _candidates[0] : null;
                _candidateIndex = 0;
            }
        }

        public void CycleTarget()
        {
            RefreshCandidates(null);
            if (_candidates.Count == 0)
            {
                CurrentTarget = null;
                return;
            }

            _candidateIndex = (_candidateIndex + 1) % _candidates.Count;
            CurrentTarget = _candidates[_candidateIndex];
        }

        public void AcquireNearest(Transform origin)
        {
            RefreshCandidates(origin);
            _candidateIndex = 0;
            CurrentTarget = _candidates.Count > 0 ? _candidates[0] : null;
        }

        private void RefreshCandidates(Transform origin)
        {
            _candidates.Clear();
            var aimOrigin = origin != null ? origin : transform;
            var forward = aimOrigin.forward;

            var hits = Physics.OverlapSphere(aimOrigin.position, lockRange, targetLayers);
            foreach (var col in hits)
            {
                var damageable = col.GetComponentInParent<IDamageable>();
                if (damageable == null || !damageable.IsAlive)
                {
                    continue;
                }

                var ownerTeam = GetComponentInParent<IDamageable>()?.Team ?? TeamId.None;
                if (ownerTeam != TeamId.None && damageable.Team == ownerTeam)
                {
                    continue;
                }

                var targetTransform = damageable is Component c ? c.transform : col.transform;
                var toTarget = (targetTransform.position - aimOrigin.position).normalized;
                if (Vector3.Angle(forward, toTarget) <= lockConeDegrees)
                {
                    _candidates.Add(targetTransform);
                }
            }

            _candidates.Sort((a, b) =>
            {
                var distA = Vector3.SqrMagnitude(a.position - aimOrigin.position);
                var distB = Vector3.SqrMagnitude(b.position - aimOrigin.position);
                return distA.CompareTo(distB);
            });
        }
    }
}
