#if UNITY_EDITOR
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using CosmicFront.AI;
using CosmicFront.Combat;
using CosmicFront.Core;
using CosmicFront.Mech;
using CosmicFront.Player;

namespace CosmicFront.Editor
{
    public static class SceneSetupWizard
    {
        [MenuItem("Cosmic Front/Setup P1 Prototype Scene")]
        public static void SetupPrototypeScene()
        {
            var scene = EditorSceneManager.NewScene(NewSceneSetup.DefaultGameObjects, NewSceneMode.Single);

            var ground = GameObject.CreatePrimitive(PrimitiveType.Cube);
            ground.name = "Platform";
            ground.transform.localScale = new Vector3(40f, 1f, 80f);
            ground.transform.position = new Vector3(0f, -0.5f, 0f);

            var managerGo = new GameObject("GameManager");
            managerGo.AddComponent<GameManager>();

            var playerMech = CreateMech("PlayerMech", TeamId.Terran, true);
            playerMech.transform.position = new Vector3(0f, 2f, -30f);
            playerMech.tag = "Player";

            var bootstrap = new GameObject("BattleBootstrap");
            var boot = bootstrap.AddComponent<BattleSceneBootstrap>();
            SetPrivateField(boot, "playerMech", playerMech.GetComponent<MechController>());

            var cam = Camera.main;
            if (cam != null)
            {
                SetPrivateField(boot, "fallbackCamera", cam);
            }

            var spawnerGo = new GameObject("EnemySpawner");
            var spawner = spawnerGo.AddComponent<EnemySpawner>();
            var enemyPrefab = CreateMechPrefabAsset();
            SetPrivateField(spawner, "enemyPrefab", enemyPrefab);
            SetPrivateField(spawner, "spawnPoints", CreateSpawnPoints());

            EditorSceneManager.SaveScene(scene, "Assets/_Project/Scenes/Map_ColonyRim.unity");
            AssetDatabase.SaveAssets();
            Debug.Log("Cosmic Front: Map_ColonyRim prototype scene created.");
        }

        private static GameObject CreateMech(string name, TeamId team, bool isPlayer)
        {
            var root = new GameObject(name);
            var rb = root.AddComponent<Rigidbody>();
            rb.mass = 500f;
            rb.drag = 2f;
            rb.angularDrag = 4f;
            rb.useGravity = false;

            var yaw = new GameObject("YawPivot").transform;
            yaw.SetParent(root.transform, false);
            var pitch = new GameObject("PitchPivot").transform;
            pitch.SetParent(yaw, false);
            var cockpit = new GameObject("CockpitAnchor").transform;
            cockpit.SetParent(pitch, false);
            cockpit.localPosition = new Vector3(0f, 1.5f, 0.5f);

            var body = GameObject.CreatePrimitive(PrimitiveType.Cube);
            body.name = "Body";
            body.transform.SetParent(pitch, false);
            body.transform.localScale = new Vector3(2f, 3f, 1.5f);
            Object.DestroyImmediate(body.GetComponent<Collider>());

            var col = root.AddComponent<BoxCollider>();
            col.size = new Vector3(2f, 3f, 1.5f);
            col.center = new Vector3(0f, 1.5f, 0f);

            var mech = root.AddComponent<MechController>();
            SetPrivateField(mech, "yawPivot", yaw);
            SetPrivateField(mech, "pitchPivot", pitch);
            SetPrivateField(mech, "fireOrigin", pitch);
            root.AddComponent<MechMovement>();
            var health = root.AddComponent<HealthSystem>();
            health.Configure(team, 100f, 50f);
            root.AddComponent<LockOnSystem>();
            root.AddComponent<WeaponPrimary>();
            root.AddComponent<WeaponSecondary>();

            if (isPlayer)
            {
                root.AddComponent<FallbackMechInput>();
            }
            else
            {
                root.AddComponent<SimpleEnemyAI>();
            }

            return root;
        }

        private static GameObject CreateMechPrefabAsset()
        {
            EnsureFolder("Assets/_Project/Prefabs");
            var temp = CreateMech("EnemyMech", TeamId.Orbital, false);
            var path = "Assets/_Project/Prefabs/EnemyMech.prefab";
            var prefab = PrefabUtility.SaveAsPrefabAsset(temp, path);
            Object.DestroyImmediate(temp);
            return prefab;
        }

        private static Transform[] CreateSpawnPoints()
        {
            var parent = new GameObject("SpawnPoints").transform;
            var points = new Transform[4];
            var offsets = new[]
            {
                new Vector3(-8f, 2f, 25f),
                new Vector3(8f, 2f, 25f),
                new Vector3(-8f, 2f, 35f),
                new Vector3(8f, 2f, 35f)
            };

            for (var i = 0; i < offsets.Length; i++)
            {
                var p = new GameObject($"Spawn_{i}").transform;
                p.SetParent(parent, false);
                p.position = offsets[i];
                points[i] = p;
            }

            return points;
        }

        private static void EnsureFolder(string path)
        {
            if (!AssetDatabase.IsValidFolder(path))
            {
                var parts = path.Split('/');
                var current = parts[0];
                for (var i = 1; i < parts.Length; i++)
                {
                    var next = current + "/" + parts[i];
                    if (!AssetDatabase.IsValidFolder(next))
                    {
                        AssetDatabase.CreateFolder(current, parts[i]);
                    }

                    current = next;
                }
            }
        }

        private static void SetPrivateField(Object target, string fieldName, object value)
        {
            var field = target.GetType().GetField(fieldName,
                System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance);
            field?.SetValue(target, value);
        }
    }
}
#endif
