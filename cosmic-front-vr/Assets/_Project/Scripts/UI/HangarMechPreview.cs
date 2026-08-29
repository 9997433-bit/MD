using UnityEngine;
using CosmicFront.AI;
using CosmicFront.Core;
using CosmicFront.Mech;

namespace CosmicFront.UI
{
    /// <summary>
    /// Rotating hangar preview that mirrors team/model dropdown selection.
    /// </summary>
    public class HangarMechPreview : MonoBehaviour
    {
        [SerializeField] private MechController previewMech;
        [SerializeField] private float yawSpeed = 22f;
        [SerializeField] private Transform turntable;

        private TeamId _team = TeamId.Terran;
        private MechModelId _model = MechModelId.Kestrel;

        private void Awake()
        {
            if (previewMech == null)
            {
                previewMech = GetComponentInChildren<MechController>();
            }

            if (turntable == null && previewMech != null)
            {
                turntable = previewMech.transform;
            }

            // Preview should not simulate physics/AI.
            if (previewMech != null)
            {
                var rb = previewMech.GetComponent<Rigidbody>();
                if (rb != null)
                {
                    rb.isKinematic = true;
                    rb.detectCollisions = false;
                }

                previewMech.enabled = false;
                var ai = previewMech.GetComponent<SimpleEnemyAI>();
                if (ai != null)
                {
                    ai.enabled = false;
                }
            }
        }

        private void Update()
        {
            if (turntable != null)
            {
                turntable.Rotate(0f, yawSpeed * Time.deltaTime, 0f, Space.World);
            }
        }

        public void Show(TeamId team, MechModelId model)
        {
            _team = team;
            _model = model;
            if (previewMech == null)
            {
                return;
            }

            previewMech.SetTeam(team);
            previewMech.SetModel(model);
        }

        public void ShowFromHangar(HangarMenu menu)
        {
            if (menu == null)
            {
                return;
            }

            Show(menu.GetSelectedTeam(), menu.GetSelectedModel());
        }
    }
}
