using UnityEngine;
using CosmicFront.Core;

namespace CosmicFront.Core
{
    public class HangarSceneBootstrap : MonoBehaviour
    {
        private void Start()
        {
            if (GameManager.Instance == null)
            {
                var go = new GameObject("GameManager");
                go.AddComponent<GameManager>();
            }

            GameManager.Instance?.OnHangarSceneLoaded();
        }
    }
}
