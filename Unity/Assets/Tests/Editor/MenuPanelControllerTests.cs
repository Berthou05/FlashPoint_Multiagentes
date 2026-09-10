using System;
using System.Reflection;
using NUnit.Framework;

public class MenuPanelControllerTests
{
    [Test]
    public void MenuControllerHasAnActionToReturnToMainMenu()
    {
        Type controllerType = Type.GetType(
            "MenuPanelController, Assembly-CSharp"
        );
        MethodInfo mainMenuAction = controllerType.GetMethod(
            "OnClickMainMenu",
            BindingFlags.Instance | BindingFlags.Public
        );

        Assert.That(mainMenuAction, Is.Not.Null);
    }
}
