using System;
using System.Reflection;
using NUnit.Framework;
using UnityEngine;

public class CameraTurnFocusTests
{
    [Test]
    public void CameraTurnFocusComponentIsAvailable()
    {
        Type componentType = Type.GetType("CameraTurnFocus, Assembly-CSharp");

        Assert.That(componentType, Is.Not.Null);
    }

    [Test]
    public void FocusPositionKeepsTheCameraNearItsOriginalComposition()
    {
        Type componentType = Type.GetType("CameraTurnFocus, Assembly-CSharp");
        MethodInfo followPositionMethod = componentType.GetMethod(
            "CalculateFollowPosition",
            BindingFlags.Public | BindingFlags.Static
        );

        Assert.That(followPositionMethod, Is.Not.Null);

        Vector3 originalPosition = new Vector3(16.8f, 24.1f, -24.2f);
        Vector3 boardCenter = new Vector3(16f, 0f, -12f);
        Vector3 doctorAtLeftEdge = new Vector3(0f, 0f, -24f);

        Vector3 result = (Vector3)followPositionMethod.Invoke(
            null,
            new object[]
            {
                originalPosition,
                boardCenter,
                doctorAtLeftEdge,
                0.3f,
                2.5f,
                2f
            }
        );

        Assert.That(result.x, Is.EqualTo(14.3f).Within(0.01f));
        Assert.That(result.y, Is.EqualTo(24.1f).Within(0.01f));
        Assert.That(result.z, Is.EqualTo(-26.2f).Within(0.01f));
    }

    [Test]
    public void DoctorTurnFocusUsesTheDoctorPositionInsteadOfKeepingTheOriginalPosition()
    {
        GameObject cameraObject = new GameObject("TestCamera");
        cameraObject.transform.position = new Vector3(10f, 20f, -10f);
        cameraObject.AddComponent<Camera>();
        CameraTurnFocus cameraFocus = cameraObject.AddComponent<CameraTurnFocus>();
        cameraFocus.followPositionFactor = 0.15f;
        cameraFocus.maxHorizontalDisplacement = 1.25f;
        cameraFocus.maxDepthDisplacement = 1f;
        cameraFocus.followSmoothTime = 0.0001f;

        MethodInfo focusMethod = typeof(CameraTurnFocus).GetMethod(
            "FocusOnDoctor",
            BindingFlags.Instance | BindingFlags.NonPublic,
            null,
            new[] { typeof(Vector3), typeof(SimulationState) },
            null
        );

        try
        {
            focusMethod.Invoke(
                cameraFocus,
                new object[]
                {
                    new Vector3(-10f, 0f, 0f),
                    new SimulationState { width = 5, height = 5 }
                }
            );

            Assert.That(cameraObject.transform.position.x, Is.LessThan(9f));
            Assert.That(cameraObject.transform.position.x, Is.GreaterThanOrEqualTo(8.75f));
        }
        finally
        {
            UnityEngine.Object.DestroyImmediate(cameraObject);
        }
    }

    [Test]
    public void EnvironmentFocusCanBeStartedForAnInfestation()
    {
        GameObject cameraObject = new GameObject("TestEnvironmentCamera");
        CameraTurnFocus cameraFocus = cameraObject.AddComponent<CameraTurnFocus>();

        MethodInfo beginEnvironmentFocus = typeof(CameraTurnFocus).GetMethod(
            "BeginEnvironmentFocus",
            BindingFlags.Instance | BindingFlags.Public
        );

        try
        {
            Assert.That(beginEnvironmentFocus, Is.Not.Null);

            beginEnvironmentFocus.Invoke(
                cameraFocus,
                new object[] { new Vector3(4f, 0f, -8f) }
            );

            FieldInfo isFocusingEnvironment = typeof(CameraTurnFocus).GetField(
                "isFocusingEnvironment",
                BindingFlags.Instance | BindingFlags.NonPublic
            );

            Assert.That(
                (bool)isFocusingEnvironment.GetValue(cameraFocus),
                Is.True
            );
        }
        finally
        {
            UnityEngine.Object.DestroyImmediate(cameraObject);
        }
    }
}
