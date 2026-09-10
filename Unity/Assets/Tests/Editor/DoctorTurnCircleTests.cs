using System;
using System.Reflection;
using NUnit.Framework;
using UnityEngine;

public class DoctorTurnCircleTests
{
    [Test]
    public void TurnCircleIsActivatedForTheDoctor()
    {
        Type rendererType = Type.GetType("SimulationRenderer, Assembly-CSharp");
        MethodInfo circleMethod = rendererType.GetMethod(
            "SetDoctorCircleActive",
            BindingFlags.Public | BindingFlags.Static
        );

        Assert.That(circleMethod, Is.Not.Null);

        GameObject doctor = new GameObject("Doctor_14");
        GameObject circle = new GameObject("DoctorCircle");
        circle.transform.SetParent(doctor.transform);
        circle.SetActive(false);

        circleMethod.Invoke(null, new object[] { doctor, true });

        Assert.That(circle.activeSelf, Is.True);

        UnityEngine.Object.DestroyImmediate(doctor);
    }
}
