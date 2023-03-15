using System;
using CmdProcessing;
using Microsoft.VisualStudio.TestTools.UnitTesting;
using System.Json;
using System.Collections.Generic;

namespace CmdProcessor_UnitTest
{
    [TestClass]
    public class UnitTest1
    {
        [TestMethod]
        public void TestInvocationAndResultOfListener()
        {
            // TEST Invoke Registered function
            // ARRANGE
            CmdProcessor p = new CmdProcessor();
            String commandValue = "exCmd";

            // ACT

            // Create the dummy listener thread function, 
            // that simply returns a JSON obj as though a command 
            // was received from some other source
            Func<JsonObject> func = () =>
            {

                // Create the dummy JSON object to return
                List<KeyValuePair<String, JsonValue>> kvList = new List<KeyValuePair<String, JsonValue>>();
                String key = CmdProcessor.JSON_CMD_NAME_ID;
                JsonValue value = commandValue;
                kvList.Add(new KeyValuePair<string, JsonValue>(key, value));
                JsonObject obj = new JsonObject(kvList);

                return obj;
            };

            // Setup listener thread function
            p.ListenerThread = func;


            // ASSERT
            JsonObject result = p.ListenerThread.Invoke();

            Console.WriteLine("Expected: {0}", commandValue);
            Console.WriteLine("Actual: {0}", (String) result[CmdProcessor.JSON_CMD_NAME_ID]);
            Assert.IsTrue(String.Compare(commandValue, (String) result[CmdProcessor.JSON_CMD_NAME_ID]) == 0);
        }

        [TestMethod]
        public void TestRunAndExecuteCommand()
        {
            // TEST Invoke Registered function
            // ARRANGE
            CmdProcessor p = new CmdProcessor();
            String commandValue = "example";

            // Create the dummy listener thread function, 
            // that simply returns a JSON obj as though a command 
            // was received from some other source
            Func<JsonObject> func = () =>
            {

                // Create the dummy JSON object to return
                List<KeyValuePair<String, JsonValue>> kvList = new List<KeyValuePair<String, JsonValue>>();
                String key = CmdProcessor.JSON_CMD_NAME_ID;
                JsonValue value = commandValue;
                kvList.Add(new KeyValuePair<string, JsonValue>(key, value));
                JsonObject obj = new JsonObject(kvList);

                return obj;
            };

            // Setup listener thread function
            p.ListenerThread = func;
            
            // ACT

            p.RegisterCmd(new ExampleCmdAction());
            p.RunCmdListenerThread();

            // ASSERT
            Assert.Inconclusive("Check the Console output for the execution of the command");
        }
    }
}
