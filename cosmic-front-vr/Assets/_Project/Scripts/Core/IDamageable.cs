using UnityEngine;

namespace CosmicFront.Core
{
    public interface IDamageable
    {
        TeamId Team { get; }
        bool IsAlive { get; }
        void ApplyDamage(float amount, GameObject source);
    }
}
