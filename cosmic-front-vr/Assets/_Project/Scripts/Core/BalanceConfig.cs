namespace CosmicFront.Core
{
    /// <summary>
    /// Central balance constants mirrored from current script defaults / presets.
    /// Documentation: docs/BALANCE_SHEET.md. Wire callers gradually; do not bulk-refactor gameplay in one pass.
    /// </summary>
    public static class BalanceConfig
    {
        public static class MechLight
        {
            public const float MaxHealth = 100f;
            public const float MaxShield = 50f;
            public const float MaxSpeed = 18f;
            public const float BoostFuel = 100f;
            public const float PrimaryDps = 30f;
        }

        public static class MechHeavy
        {
            public const float MaxHealth = 200f;
            public const float MaxShield = 80f;
            public const float MaxSpeed = 12f;
            public const float BoostFuel = 70f;
            public const float PrimaryDps = 45f;
        }

        public static class MechWarden
        {
            public const float MaxHealth = 110f;
            public const float MaxShield = 70f;
            public const float MaxSpeed = 14f;
            public const float BoostFuel = 90f;
            public const float PrimaryDps = 18f;
        }

        public static class MechMediator
        {
            public const float MaxHealth = 140f;
            public const float MaxShield = 90f;
            public const float MaxSpeed = 15f;
            public const float BoostFuel = 85f;
            public const float PrimaryDps = 32f;
        }

        public static class MechBeacon
        {
            public const float MaxHealth = 80f;
            public const float MaxShield = 40f;
            public const float MaxSpeed = 20f;
            public const float BoostFuel = 110f;
            public const float PrimaryDps = 22f;
        }

        public static class MechMovementDefaults
        {
            public const float Acceleration = 35f;
            public const float VerticalSpeed = 12f;
            public const float BoostMultiplier = 1.8f;
            public const float Drag = 2f;
            public const float YawRate = 90f;
            public const float PitchRate = 45f;
            public const float MaxPitch = 30f;
            public const float BoostDrainPerSecond = 25f;
            public const float BoostRegenPerSecond = 15f;
        }

        public static class WeaponPrimaryDefaults
        {
            public const float FireRate = 8f;
            public const float Range = 150f;
            public const float HomingAssist = 0.15f;
        }

        public static class WeaponSecondaryDefaults
        {
            public const float FireCooldown = 1.2f;
            public const int MaxAmmo = 4;
            public const float ReloadTime = 4f;
            public const float ProjectileSpeed = 40f;
            public const float ProjectileDamage = 25f;
        }

        public static class LockOnDefaults
        {
            public const float ConeDegrees = 15f;
            public const float Range = 200f;
        }

        public static class HealthDefaults
        {
            public const float ShieldRegenDelay = 3f;
            public const float ShieldRegenRate = 10f;
        }

        public static class ShipFrigate
        {
            public const float MaxHealth = 500f;
            public const float MaxShield = 200f;
        }

        public static class ShipCruiser
        {
            public const float MaxHealth = 800f;
            public const float MaxShield = 300f;
        }

        public static class ShipMovementDefaults
        {
            public const float MaxSpeed = 8f;
            public const float Acceleration = 12f;
            public const float VerticalSpeed = 5f;
            public const float YawRate = 35f;
            public const float PitchRate = 20f;
            public const float MaxPitch = 20f;
            public const float BoostMultiplier = 1.4f;
            public const float MaxBoostFuel = 80f;
            public const float BoostDrain = 18f;
            public const float BoostRegen = 10f;
        }

        public static class ShipTurretDefaults
        {
            public const float FireRate = 4f;
            public const float Damage = 18f;
            public const float Range = 220f;
        }

        public static class ShipCaptainDefaults
        {
            public const float AbilityCooldown = 45f;
            public const float ShieldBoostAmount = 80f;
            public const float AbilityDuration = 8f;
        }

        public static class ShipLaunchDefaults
        {
            public const float LaunchImpulse = 25f;
            public const float CooldownSeconds = 8f;
        }

        public static class MatchDefaults
        {
            public const float DurationSeconds = 600f;
            public const float RespawnDelaySeconds = 10f;
        }

        public static class EscortDefaults
        {
            public const float CruiseSpeed = 4f;
            public const float WaypointReachDistance = 5f;
            public const float FlagshipHealth = 1200f;
            public const float FlagshipShield = 400f;
        }

        public static class CaptureDefaults
        {
            public const float Radius = 12f;
            public const float CaptureRate = 0.25f;
            public const float ScoreTickInterval = 2f;
            public const int ScoreLimit = 100;
        }

        public static class EnemyAiDefaults
        {
            public const float DetectRange = 120f;
            public const float AttackRange = 60f;
            public const float StrafeStrength = 0.6f;
            public const int InitialSpawnCount = 6;
            public const float RespawnDelay = 8f;
        }
    }
}
