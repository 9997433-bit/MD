#if UNITY_EDITOR
using UnityEditor;
using UnityEngine;

namespace Aetherboard.Editor
{
    public static class OpenXRProjectWizard
    {
        [MenuItem("Aetherboard/Configure Quest (Android) Build Settings")]
        public static void ConfigureQuestBuild()
        {
            PlayerSettings.companyName = "Aetherboard";
            PlayerSettings.productName = "Aetherboard VR";
            EditorUserBuildSettings.SwitchActiveBuildTarget(
                BuildTargetGroup.Android, BuildTarget.Android);

            PlayerSettings.Android.minSdkVersion = AndroidSdkVersions.AndroidApiLevel29;
            PlayerSettings.SetScriptingBackend(BuildTargetGroup.Android, ScriptingImplementation.IL2CPP);
            PlayerSettings.Android.targetArchitectures = AndroidArchitecture.ARM64;
            PlayerSettings.colorSpace = ColorSpace.Linear;

            PlayerSettings.virtualRealitySupported = false;
            Debug.Log(
                "Aetherboard: Android/ARM64/IL2CPP configured. " +
                "Next: Install OpenXR + XR Interaction Toolkit, enable OpenXR in XR Plug-in Management, " +
                "add Oculus Touch / Meta Quest Touch Plus interaction profiles.");
        }

        [MenuItem("Aetherboard/Configure PCVR (Standalone) Build Settings")]
        public static void ConfigurePcvrBuild()
        {
            EditorUserBuildSettings.SwitchActiveBuildTarget(
                BuildTargetGroup.Standalone, BuildTarget.StandaloneWindows64);
            PlayerSettings.colorSpace = ColorSpace.Linear;
            Debug.Log("Aetherboard: PCVR Windows x64 configured. Enable OpenXR + SteamVR or Oculus PC profile.");
        }
    }
}
#endif
