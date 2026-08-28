#if UNITY_EDITOR
using System.Collections.Generic;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.UI;
using CosmicFront.AI;
using CosmicFront.Combat;
using CosmicFront.Core;
using CosmicFront.Mech;
using CosmicFront.Network;
using CosmicFront.Player;
using CosmicFront.UI;
using FishNet.Component.Transforming;
using FishNet.Managing;
using FishNet.Managing.Object;
using FishNet.Object;
using FishNet.Transporting.Tugboat;

namespace CosmicFront.Editor
{
    public static class SceneSetupWizard
    {
        private const string HangarScenePath = "Assets/_Project/Scenes/Hangar.unity";
        private const string BattleScenePath = "Assets/_Project/Scenes/Map_ColonyRim.unity";

        [MenuItem("Cosmic Front/Setup All Scenes (Hangar + Battle)")]
        public static void SetupAllScenes()
        {
            EnsureFolder("Assets/_Project/Scenes");
            EnsureFolder("Assets/_Project/Prefabs");

            SetupHangarSceneInternal();
            SetupPrototypeSceneInternal();
            ConfigureBuildSettings();

            AssetDatabase.SaveAssets();
            Debug.Log("Cosmic Front: Hangar + Map_ColonyRim scenes ready. Build Settings updated.");
        }

        [MenuItem("Cosmic Front/Setup P1 Prototype Scene")]
        public static void SetupPrototypeScene()
        {
            SetupPrototypeSceneInternal();
            ConfigureBuildSettings();
            AssetDatabase.SaveAssets();
            Debug.Log("Cosmic Front: Map_ColonyRim prototype scene created.");
        }

        [MenuItem("Cosmic Front/Setup Hangar Scene")]
        public static void SetupHangarScene()
        {
            SetupHangarSceneInternal();
            ConfigureBuildSettings();
            AssetDatabase.SaveAssets();
            Debug.Log("Cosmic Front: Hangar scene created.");
        }

        [MenuItem("Cosmic Front/Configure Build Settings")]
        public static void ConfigureBuildSettingsMenu()
        {
            ConfigureBuildSettings();
            Debug.Log("Cosmic Front: Build settings scenes registered.");
        }

        private static void SetupHangarSceneInternal()
        {
            var scene = EditorSceneManager.NewScene(NewSceneSetup.DefaultGameObjects, NewSceneMode.Single);

            var floor = GameObject.CreatePrimitive(PrimitiveType.Cube);
            floor.name = "HangarFloor";
            floor.transform.localScale = new Vector3(30f, 0.2f, 20f);
            floor.transform.position = new Vector3(0f, -0.1f, 0f);

            var managerGo = new GameObject("GameManager");
            managerGo.AddComponent<GameManager>();

            var bootstrap = new GameObject("HangarBootstrap");
            bootstrap.AddComponent<HangarSceneBootstrap>();

            var previewMech = CreateMech("PreviewMech", TeamId.Terran, false);
            previewMech.transform.position = new Vector3(-6f, 0f, 2f);
            Object.DestroyImmediate(previewMech.GetComponent<Rigidbody>());
            Object.DestroyImmediate(previewMech.GetComponent<SimpleEnemyAI>());

            CreateHangarUi();
            CreateXRRig(new Vector3(0f, 0f, -6f), null);
            CreateFishNetNetworkManager();

            DisableDefaultMainCamera();

            EditorSceneManager.SaveScene(scene, HangarScenePath);
        }

        private static void SetupPrototypeSceneInternal()
        {
            var scene = EditorSceneManager.NewScene(NewSceneSetup.DefaultGameObjects, NewSceneMode.Single);

            var ground = GameObject.CreatePrimitive(PrimitiveType.Cube);
            ground.name = "Platform";
            ground.transform.localScale = new Vector3(40f, 1f, 80f);
            ground.transform.position = new Vector3(0f, -0.5f, 0f);

            CreateRimWalls();

            if (GameObject.Find("GameManager") == null)
            {
                var managerGo = new GameObject("GameManager");
                managerGo.AddComponent<GameManager>();
            }

            var playerMech = CreateMech("PlayerMech", TeamId.Terran, true);
            playerMech.transform.position = new Vector3(0f, 2f, -30f);
            playerMech.tag = "Player";

            var cockpit = playerMech.transform.Find("YawPivot/PitchPivot/CockpitAnchor");
            var xrRig = CreateXRRig(new Vector3(0f, 2f, -30f), cockpit);
            var binder = xrRig.GetComponent<PlayerMechBinder>();
            SetPrivateField(binder, "mech", playerMech.GetComponent<MechController>());
            SetPrivateField(binder, "cockpitAnchor", cockpit);

            var comfort = xrRig.GetComponent<VRComfortSettings>();
            CreateBoostVignette(comfort, xrRig.transform);

            var bootstrapGo = new GameObject("BattleBootstrap");
            var boot = bootstrapGo.AddComponent<BattleSceneBootstrap>();
            SetPrivateField(boot, "playerMech", playerMech.GetComponent<MechController>());
            var xrSetup = xrRig.GetComponent<XROriginSetup>();
            SetPrivateField(boot, "fallbackCamera", xrSetup != null ? xrSetup.VrCamera : null);

            CreateBattleHud(xrRig.transform, playerMech.GetComponent<MechController>());
            CreateMatchResultsUi();

            var spawnerGo = new GameObject("EnemySpawner");
            var spawner = spawnerGo.AddComponent<EnemySpawner>();
            var enemyPrefab = CreateMechPrefabAsset();
            SetPrivateField(spawner, "enemyPrefab", enemyPrefab);
            var spawnPoints = CreateSpawnPoints();
            SetPrivateField(spawner, "spawnPoints", spawnPoints);
            var playerNetworkPrefab = CreateNetworkPlayerPrefabAsset();
            CreateNetworkMatchManager(playerNetworkPrefab, spawnPoints, playerMech);

            DisableDefaultMainCamera();

            EditorSceneManager.SaveScene(scene, BattleScenePath);
        }

        private static GameObject CreateXRRig(Vector3 position, Transform cockpitAnchor)
        {
            var rig = new GameObject("XROrigin");
            rig.transform.position = position;

            rig.AddComponent<XROriginSetup>();
            rig.AddComponent<VRComfortSettings>();
            rig.AddComponent<VRSnapTurn>();
            var binder = rig.AddComponent<PlayerMechBinder>();
            if (cockpitAnchor != null)
            {
                SetPrivateField(binder, "cockpitAnchor", cockpitAnchor);
            }

            var setup = rig.GetComponent<XROriginSetup>();
            setup.EnsureHierarchy();
            return rig;
        }

        private static void CreateHangarUi()
        {
            var canvasGo = new GameObject("HangarCanvas");
            var canvas = canvasGo.AddComponent<Canvas>();
            canvas.renderMode = RenderMode.ScreenSpaceOverlay;
            canvasGo.AddComponent<CanvasScaler>().uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
            canvasGo.AddComponent<GraphicRaycaster>();

            var panel = CreateUiPanel(canvasGo.transform, new Vector2(460f, 420f), new Vector2(0.5f, 0.5f));

            var title = CreateText(panel.transform, "Title", "COSMIC FRONT VR", 22, TextAnchor.UpperCenter);
            title.rectTransform.anchoredPosition = new Vector2(0f, -10f);
            title.rectTransform.sizeDelta = new Vector2(420f, 40f);

            var teamDropdown = CreateDropdown(panel.transform, "TeamDropdown", new Vector2(0f, -60f));
            var mechDropdown = CreateDropdown(panel.transform, "MechDropdown", new Vector2(0f, -110f));

            var startBtn = CreateButton(panel.transform, "StartButton", "单机开始", new Vector2(-110f, -170f), new Vector2(180f, 36f));
            var hostBtn = CreateButton(panel.transform, "HostButton", "Host 局域网", new Vector2(110f, -170f), new Vector2(180f, 36f));
            var joinBtn = CreateButton(panel.transform, "JoinButton", "Join 局域网", new Vector2(0f, -220f), new Vector2(200f, 36f));

            var addressInput = CreateInputField(panel.transform, "AddressInput", "127.0.0.1", new Vector2(0f, -270f));

            var status = CreateText(panel.transform, "Status", "单机或多人 LAN（端口 7770）", 14, TextAnchor.MiddleCenter);
            status.rectTransform.anchoredPosition = new Vector2(0f, -320f);
            status.rectTransform.sizeDelta = new Vector2(420f, 30f);

            var hint = CreateText(panel.transform, "ControlsHint", "", 11, TextAnchor.LowerCenter);
            hint.rectTransform.anchoredPosition = new Vector2(0f, -370f);
            hint.rectTransform.sizeDelta = new Vector2(440f, 40f);
            hint.color = new Color(0.75f, 0.85f, 1f);

            var menu = canvasGo.AddComponent<HangarMenu>();
            SetPrivateField(menu, "teamDropdown", teamDropdown);
            SetPrivateField(menu, "mechDropdown", mechDropdown);
            SetPrivateField(menu, "startButton", startBtn);
            SetPrivateField(menu, "hostButton", hostBtn);
            SetPrivateField(menu, "joinButton", joinBtn);
            SetPrivateField(menu, "addressInput", addressInput);
            SetPrivateField(menu, "statusText", status);
            SetPrivateField(menu, "controlsHint", hint);
        }

        private static void CreateFishNetNetworkManager()
        {
            if (Object.FindObjectOfType<NetworkManager>() != null)
            {
                return;
            }

            var go = new GameObject("NetworkManager");
            var nm = go.AddComponent<NetworkManager>();
            var transport = go.AddComponent<Tugboat>();
            transport.SetPort(NetworkSessionConfig.Port);

            var dpo = EnsureDefaultPrefabObjects();
            SetPrivateField(nm, "_defaultPrefabObjects", dpo);
            Object.DontDestroyOnLoad(go);
        }

        private static DefaultPrefabObjects EnsureDefaultPrefabObjects()
        {
            const string path = "Assets/_Project/Settings/DefaultPrefabObjects.asset";
            EnsureFolder("Assets/_Project/Settings");
            var existing = AssetDatabase.LoadAssetAtPath<DefaultPrefabObjects>(path);
            if (existing != null)
            {
                return existing;
            }

            var dpo = ScriptableObject.CreateInstance<DefaultPrefabObjects>();
            AssetDatabase.CreateAsset(dpo, path);
            return dpo;
        }

        private static GameObject CreateNetworkPlayerPrefabAsset()
        {
            EnsureFolder("Assets/_Project/Prefabs");
            var temp = CreateMech("NetworkPlayerMech", TeamId.Terran, true);
            temp.tag = "Player";
            temp.AddComponent<NetworkObject>();
            temp.AddComponent<NetworkTransform>();
            temp.AddComponent<NetworkMechSync>();

            var path = "Assets/_Project/Prefabs/NetworkPlayerMech.prefab";
            var prefab = PrefabUtility.SaveAsPrefabAsset(temp, path);
            Object.DestroyImmediate(temp);

            RegisterNetworkPrefab(prefab);
            return prefab;
        }

        private static void RegisterNetworkPrefab(GameObject prefab)
        {
            var nob = prefab.GetComponent<NetworkObject>();
            if (nob == null)
            {
                return;
            }

            var dpo = EnsureDefaultPrefabObjects();
            dpo.AddObject(nob, checkDuplicates: true, spawnable: true);
            EditorUtility.SetDirty(dpo);
        }

        private static void CreateNetworkMatchManager(GameObject playerPrefab, Transform[] spawnPoints, GameObject singlePlayerMech)
        {
            var go = new GameObject("NetworkMatchManager");
            go.AddComponent<NetworkObject>();
            var match = go.AddComponent<NetworkMatchManager>();

            var nob = playerPrefab.GetComponent<NetworkObject>();
            SetPrivateField(match, "playerPrefab", nob);
            SetPrivateField(match, "spawnPoints", spawnPoints);
            SetPrivateField(match, "singlePlayerMechToDisable", singlePlayerMech);
        }

        private static void CreateBattleHud(Transform parent, MechController mech)
        {
            var canvasGo = new GameObject("CockpitHUD");
            canvasGo.transform.SetParent(parent, false);
            canvasGo.transform.localPosition = new Vector3(0f, 0f, 0.4f);
            canvasGo.transform.localScale = Vector3.one * 0.001f;

            var canvas = canvasGo.AddComponent<Canvas>();
            canvas.renderMode = RenderMode.WorldSpace;
            var rect = canvasGo.GetComponent<RectTransform>();
            rect.sizeDelta = new Vector2(800f, 400f);

            var healthBar = CreateSlider(canvasGo.transform, "HealthBar", new Vector2(-200f, 150f), Color.red);
            var shieldBar = CreateSlider(canvasGo.transform, "ShieldBar", new Vector2(-200f, 120f), Color.cyan);
            var boostBar = CreateSlider(canvasGo.transform, "BoostBar", new Vector2(-200f, 90f), Color.yellow);
            var lockText = CreateText(canvasGo.transform, "Lock", "---", 18, TextAnchor.MiddleCenter);
            lockText.rectTransform.anchoredPosition = new Vector2(200f, 150f);
            var speedText = CreateText(canvasGo.transform, "Speed", "0 m/s", 16, TextAnchor.MiddleCenter);
            speedText.rectTransform.anchoredPosition = new Vector2(200f, 120f);

            var hud = canvasGo.AddComponent<CockpitHUD>();
            SetPrivateField(hud, "healthBar", healthBar);
            SetPrivateField(hud, "shieldBar", shieldBar);
            SetPrivateField(hud, "boostBar", boostBar);
            SetPrivateField(hud, "lockIndicator", lockText);
            SetPrivateField(hud, "speedLabel", speedText);
            SetPrivateField(hud, "mech", mech);
        }

        private static void CreateMatchResultsUi()
        {
            var canvasGo = new GameObject("ResultsCanvas");
            var canvas = canvasGo.AddComponent<Canvas>();
            canvas.renderMode = RenderMode.ScreenSpaceOverlay;
            canvasGo.AddComponent<CanvasScaler>().uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
            canvasGo.AddComponent<GraphicRaycaster>();

            var panel = CreateUiPanel(canvasGo.transform, new Vector2(360f, 220f), new Vector2(0.5f, 0.5f));
            panel.SetActive(false);

            var kills = CreateText(panel.transform, "Kills", "击坠: 0", 16, TextAnchor.UpperCenter);
            kills.rectTransform.anchoredPosition = new Vector2(0f, -40f);
            var deaths = CreateText(panel.transform, "Deaths", "被击坠: 0", 16, TextAnchor.UpperCenter);
            deaths.rectTransform.anchoredPosition = new Vector2(0f, -80f);
            var returnBtn = CreateButton(panel.transform, "ReturnButton", "返回机库", new Vector2(0f, -140f));

            var results = canvasGo.AddComponent<MatchResultsUI>();
            SetPrivateField(results, "panel", panel);
            SetPrivateField(results, "killsText", kills);
            SetPrivateField(results, "deathsText", deaths);
            SetPrivateField(results, "returnButton", returnBtn);
        }

        private static void CreateBoostVignette(VRComfortSettings comfort, Transform parent)
        {
            var canvasGo = new GameObject("BoostVignette");
            canvasGo.transform.SetParent(parent, false);
            var canvas = canvasGo.AddComponent<Canvas>();
            canvas.renderMode = RenderMode.ScreenSpaceOverlay;
            canvas.sortingOrder = 100;

            var image = new GameObject("Vignette").AddComponent<Image>();
            image.transform.SetParent(canvasGo.transform, false);
            image.color = new Color(0f, 0f, 0f, 0f);
            var rect = image.GetComponent<RectTransform>();
            rect.anchorMin = Vector2.zero;
            rect.anchorMax = Vector2.one;
            rect.offsetMin = Vector2.zero;
            rect.offsetMax = Vector2.zero;

            var group = canvasGo.AddComponent<CanvasGroup>();
            group.alpha = 0f;
            group.blocksRaycasts = false;

            SetPrivateField(comfort, "boostVignette", group);
        }

        private static void CreateRimWalls()
        {
            CreateWall("WallLeft", new Vector3(-21f, 5f, 0f), new Vector3(1f, 10f, 82f));
            CreateWall("WallRight", new Vector3(21f, 5f, 0f), new Vector3(1f, 10f, 82f));
        }

        private static void CreateWall(string name, Vector3 pos, Vector3 scale)
        {
            var wall = GameObject.CreatePrimitive(PrimitiveType.Cube);
            wall.name = name;
            wall.transform.position = pos;
            wall.transform.localScale = scale;
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
                root.AddComponent<VRMechInput>();
                root.AddComponent<MechInputRouter>();
                root.AddComponent<MechBoostFeedback>();
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

        private static void ConfigureBuildSettings()
        {
            var scenes = new List<EditorBuildSettingsScene>();
            if (System.IO.File.Exists(HangarScenePath))
            {
                scenes.Add(new EditorBuildSettingsScene(HangarScenePath, true));
            }

            if (System.IO.File.Exists(BattleScenePath))
            {
                scenes.Add(new EditorBuildSettingsScene(BattleScenePath, true));
            }

            EditorBuildSettings.scenes = scenes.ToArray();
        }

        private static void DisableDefaultMainCamera()
        {
            var main = Camera.main;
            if (main != null && main.transform.root.name != "XROrigin")
            {
                main.gameObject.SetActive(false);
            }
        }

        private static GameObject CreateUiPanel(Transform parent, Vector2 size, Vector2 anchor)
        {
            var panel = new GameObject("Panel");
            panel.transform.SetParent(parent, false);
            var image = panel.AddComponent<Image>();
            image.color = new Color(0.08f, 0.1f, 0.16f, 0.92f);
            var rect = panel.GetComponent<RectTransform>();
            rect.sizeDelta = size;
            rect.anchorMin = anchor;
            rect.anchorMax = anchor;
            rect.pivot = new Vector2(0.5f, 0.5f);
            return panel;
        }

        private static Text CreateText(Transform parent, string name, string content, int fontSize, TextAnchor anchor)
        {
            var go = new GameObject(name);
            go.transform.SetParent(parent, false);
            var text = go.AddComponent<Text>();
            text.text = content;
            text.font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
            text.fontSize = fontSize;
            text.alignment = anchor;
            text.color = Color.white;
            var rect = text.rectTransform;
            rect.sizeDelta = new Vector2(360f, 30f);
            return text;
        }

        private static Button CreateButton(Transform parent, string name, string label, Vector2 pos, Vector2? size = null)
        {
            var go = new GameObject(name);
            go.transform.SetParent(parent, false);
            var image = go.AddComponent<Image>();
            image.color = new Color(0.2f, 0.45f, 0.85f);
            var btn = go.AddComponent<Button>();
            var rect = go.GetComponent<RectTransform>();
            rect.sizeDelta = size ?? new Vector2(200f, 40f);
            rect.anchoredPosition = pos;

            var textGo = new GameObject("Text");
            textGo.transform.SetParent(go.transform, false);
            var text = textGo.AddComponent<Text>();
            text.text = label;
            text.font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
            text.alignment = TextAnchor.MiddleCenter;
            text.color = Color.white;
            var textRect = text.rectTransform;
            textRect.anchorMin = Vector2.zero;
            textRect.anchorMax = Vector2.one;
            textRect.offsetMin = Vector2.zero;
            textRect.offsetMax = Vector2.zero;

            return btn;
        }

        private static InputField CreateInputField(Transform parent, string name, string defaultValue, Vector2 pos)
        {
            var go = new GameObject(name);
            go.transform.SetParent(parent, false);
            var image = go.AddComponent<Image>();
            image.color = new Color(0.12f, 0.14f, 0.2f);
            var input = go.AddComponent<InputField>();
            var rect = go.GetComponent<RectTransform>();
            rect.sizeDelta = new Vector2(280f, 32f);
            rect.anchoredPosition = pos;

            var textGo = new GameObject("Text");
            textGo.transform.SetParent(go.transform, false);
            var text = textGo.AddComponent<Text>();
            text.font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
            text.color = Color.white;
            text.supportRichText = false;
            text.alignment = TextAnchor.MiddleLeft;
            var textRect = text.rectTransform;
            textRect.anchorMin = Vector2.zero;
            textRect.anchorMax = Vector2.one;
            textRect.offsetMin = new Vector2(10f, 0f);
            textRect.offsetMax = new Vector2(-10f, 0f);

            var placeholderGo = new GameObject("Placeholder");
            placeholderGo.transform.SetParent(go.transform, false);
            var placeholder = placeholderGo.AddComponent<Text>();
            placeholder.font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
            placeholder.text = "Host IP";
            placeholder.color = new Color(1f, 1f, 1f, 0.35f);
            placeholder.alignment = TextAnchor.MiddleLeft;
            var phRect = placeholder.rectTransform;
            phRect.anchorMin = Vector2.zero;
            phRect.anchorMax = Vector2.one;
            phRect.offsetMin = new Vector2(10f, 0f);
            phRect.offsetMax = new Vector2(-10f, 0f);

            input.textComponent = text;
            input.placeholder = placeholder;
            input.text = defaultValue;

            return input;
        }

        private static Dropdown CreateDropdown(Transform parent, string name, Vector2 pos)
        {
            var go = new GameObject(name);
            go.transform.SetParent(parent, false);
            var image = go.AddComponent<Image>();
            image.color = new Color(0.15f, 0.18f, 0.25f);
            var dropdown = go.AddComponent<Dropdown>();
            var rect = go.GetComponent<RectTransform>();
            rect.sizeDelta = new Vector2(320f, 36f);
            rect.anchoredPosition = pos;

            var labelGo = new GameObject("Label");
            labelGo.transform.SetParent(go.transform, false);
            var label = labelGo.AddComponent<Text>();
            label.font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
            label.color = Color.white;
            dropdown.captionText = label;
            var labelRect = label.rectTransform;
            labelRect.anchorMin = Vector2.zero;
            labelRect.anchorMax = Vector2.one;
            labelRect.offsetMin = new Vector2(10f, 0f);
            labelRect.offsetMax = new Vector2(-30f, 0f);

            var template = new GameObject("Template");
            template.transform.SetParent(go.transform, false);
            template.SetActive(false);
            var templateRect = template.AddComponent<RectTransform>();
            templateRect.sizeDelta = new Vector2(320f, 120f);

            dropdown.template = templateRect;
            return dropdown;
        }

        private static Slider CreateSlider(Transform parent, string name, Vector2 pos, Color fillColor)
        {
            var go = new GameObject(name);
            go.transform.SetParent(parent, false);
            var slider = go.AddComponent<Slider>();
            var rect = go.GetComponent<RectTransform>();
            rect.sizeDelta = new Vector2(200f, 16f);
            rect.anchoredPosition = pos;

            var bg = new GameObject("Background").AddComponent<Image>();
            bg.transform.SetParent(go.transform, false);
            bg.color = new Color(0.2f, 0.2f, 0.2f);
            var bgRect = bg.rectTransform;
            bgRect.anchorMin = Vector2.zero;
            bgRect.anchorMax = Vector2.one;
            bgRect.offsetMin = Vector2.zero;
            bgRect.offsetMax = Vector2.zero;

            var fillArea = new GameObject("Fill Area").AddComponent<RectTransform>();
            fillArea.transform.SetParent(go.transform, false);
            fillArea.anchorMin = Vector2.zero;
            fillArea.anchorMax = Vector2.one;

            var fill = new GameObject("Fill").AddComponent<Image>();
            fill.transform.SetParent(fillArea.transform, false);
            fill.color = fillColor;

            slider.fillRect = fill.rectTransform;
            slider.targetGraphic = bg;
            slider.maxValue = 1f;
            slider.value = 1f;

            return slider;
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
