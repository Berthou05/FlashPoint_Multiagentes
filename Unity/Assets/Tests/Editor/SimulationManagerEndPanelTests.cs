using System;
using System.Reflection;
using NUnit.Framework;
using UnityEngine;

public class SimulationManagerEndPanelTests
{
    [Test]
    public void VictoryStatusShowsOnlyTheVictoryPanel()
    {
        Type managerType = Type.GetType(
            "SimulationManager, Assembly-CSharp"
        );
        MethodInfo showEndPanel = managerType.GetMethod(
            "ShowEndPanel",
            BindingFlags.Instance | BindingFlags.Public
        );

        Assert.That(showEndPanel, Is.Not.Null);

        GameObject managerObject = new GameObject("SimulationManager");
        GameObject victoryPanel = new GameObject("Victory");
        GameObject defeatPanel = new GameObject("Defeat");
        SimulationManager manager =
            managerObject.AddComponent<SimulationManager>();

        try
        {
            manager.victoryPanel = victoryPanel;
            manager.defeatPanel = defeatPanel;
            defeatPanel.SetActive(true);

            showEndPanel.Invoke(manager, new object[] { "victory" });

            Assert.That(victoryPanel.activeSelf, Is.True);
            Assert.That(defeatPanel.activeSelf, Is.False);
        }
        finally
        {
            UnityEngine.Object.DestroyImmediate(managerObject);
            UnityEngine.Object.DestroyImmediate(victoryPanel);
            UnityEngine.Object.DestroyImmediate(defeatPanel);
        }
    }
}
