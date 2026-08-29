namespace CosmicFront.Core
{
    public enum TeamId
    {
        None = 0,
        Terran = 1,
        Orbital = 2,
        Neutral = 3
    }

    public enum MechArchetype
    {
        Light,
        Heavy,
        Support,
        Balanced,
        Scout
    }

    /// <summary>
    /// Concrete mech models from IP bible (target roster).
    /// </summary>
    public enum MechModelId
    {
        Kestrel = 0,   // MS-L1 迅影 — Light
        Bastion = 1,   // MS-H1 重盾 — Heavy
        Warden = 2,    // NF-S1 守望 — Support
        Mediator = 3,  // NF-A1 仲裁 — Balanced
        Beacon = 4     // NF-C1 航标 — Scout
    }

    public enum SpawnPreference
    {
        Mech,
        ShipPilot,
        ShipGunner,
        ShipCaptain
    }

    public enum GameModeType
    {
        TeamDeathmatch = 0,
        EscortFlagship = 1,
        CapturePoints = 2
    }

    public enum GamePhase
    {
        Boot,
        Hangar,
        Loading,
        Battle,
        Results
    }
}
