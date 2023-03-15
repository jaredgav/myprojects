using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Json;

namespace CmdProcessing
{
    public class CmdProcessor
    {
        /** <summary>
         * The string found in the JSON object providing the command name
         * </summary>
         */
        public static string JSON_CMD_NAME_ID = "cmdName";

        private Dictionary<String, BaseCmdAction> registeredActions;

        /** <summary>
         * Provides a custom listener thread to be executed
         * </summary>
         * <returns>JSON object containing the command to run</returns>
         */
        public Func<JsonObject> ListenerThread { get; set; }

        public CmdProcessor()
        {
            registeredActions = new Dictionary<string, BaseCmdAction>();
        }

        /** <summary> 
         * Add a new command to the registered actions list
         * </summary>
         */
        public void RegisterCmd(BaseCmdAction cmd)
        {
            registeredActions.Add(cmd.CmdStr, cmd);
        }

        /** <summary>
         * Executes the cmd, passing along the JSON
         * object for what the command should do
         * </summary> 
         */
        void ExecuteFunc(String key, JsonObject keyValues)
        {
            registeredActions[key].Execute(keyValues);
        }

        /** <summary>
         * Starts the thread that listens for a new command
         * </summary> */
        public void RunCmdListenerThread()
        {
            //ListenerThread = ExampleListenerThread;
            if(ListenerThread != null)
            {
                JsonObject cmdObj = ListenerThread.Invoke();
                ExecuteFunc(cmdObj[JSON_CMD_NAME_ID], cmdObj);
            }
            else
            {
                throw new Exception("ListenerThread Action has not been initialized.");
            }
        }

        /**<summary>
         * An example function of what the ListenerThreadShould do
         * </summary> 
         */
        private void ExampleListenerThread()
        {
            while(true)
            {
                Console.WriteLine("Waiting for new command...");
                // Implement some sort of listener
                String userInput = Console.ReadLine();
                Console.WriteLine("Command received: {0}", userInput);
                ExecuteFunc(userInput, new JsonObject());

            }
        }
    }
}
