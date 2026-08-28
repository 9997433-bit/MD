using UnityEngine;
using CosmicFront.Core;
using CosmicFront.Mech;
using CosmicFront.Network;
using FishNet;

namespace CosmicFront.AI
{
    public class EnemySpawner : MonoBehaviour
    {
        [SerializeField] private GameObject enemyPrefab;
        [SerializeField] private int initialCount = 6;
        [SerializeField] private float respawnDelay = 8f;
        [SerializeField] private Transform[] spawnPoints;
        [SerializeField] private TeamId enemyTeam = TeamId.Orbital;

        private int _living;

        private void Start()
        {
            if (ShouldDisableOnClient())
            {
                enabled = false;
                return;
            }

            for (var i = 0; i < initialCount; i++)
            {
                SpawnOne();
            }
        }

        private static bool ShouldDisableOnClient()
        {
            var nm = InstanceFinder.NetworkManager;
            return nm != null && nm.IsClientStarted && !nm.IsServerStarted;
        }

        private void SpawnOne()
        {
            if (enemyPrefab == null || spawnPoints == null || spawnPoints.Length == 0)
            {
                return;
            }

            var point = spawnPoints[Random.Range(0, spawnPoints.Length)];
            var go = Instantiate(enemyPrefab, point.position, point.rotation);
            var mech = go.GetComponent<MechController>();
            if (mech != null)
            {
                mech.SetTeam(enemyTeam);
            }

            var health = go.GetComponent<HealthSystem>();
            if (health != null)
            {
                health.Died += OnEnemyDied;
            }

            _living++;
        }

        private void OnEnemyDied(HealthSystem health, GameObject killer)
        {
            health.Died -= OnEnemyDied;
            _living--;

            if (killer != null && killer.CompareTag("Player"))
            {
                if (GameManager.Instance != null && GameManager.Instance.IsMultiplayer &&
                    NetworkBootstrap.IsServer && NetworkScoreManager.Instance != null)
                {
                    NetworkScoreManager.Instance.RegisterFrag(killer, health.gameObject);
                }
                else if (GameManager.Instance != null && !GameManager.Instance.IsMultiplayer)
                {
                    GameManager.Instance.RegisterKill();
                }
            }

            Destroy(health.gameObject, 2f);
            Invoke(nameof(SpawnOne), respawnDelay);
        }
    }
}
