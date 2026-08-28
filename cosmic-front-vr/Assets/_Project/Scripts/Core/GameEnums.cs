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
        Heavy
    }

    public enum SpawnPreference
    {
        Mech,
        ShipPilot,
        ShipGunner,
        ShipCaptain
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
