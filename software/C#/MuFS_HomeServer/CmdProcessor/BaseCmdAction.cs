using System;
using System.Collections.Generic;
using System.Json;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace CmdProcessing
{
    /**<summary>
     * Abstract base class for all actions to be executed by the CmdProcessor
     * </summary> */
    public abstract class BaseCmdAction
    {
        /** <summary>
         * The string representation of the command
         * </summary> 
         */
        public abstract String CmdStr { get; set; }

        /** <summary>
         * The number of expected arguments 
         * </summary>
         */
        public abstract int NumArgs { get; set; }

        /** <summary>
         * Executes the commands action based on the JSON objects input
         * </summary> 
         */
        public abstract void Execute(JsonObject keyValues);
    }

    public class ExampleCmdAction : BaseCmdAction
    {
        public override string CmdStr { get; set; }
        public override int NumArgs { get; set; }

        public ExampleCmdAction()
        {
            CmdStr = "example";
            NumArgs = 1;
        }

        public override void Execute(JsonObject keyValues)
        {
            Console.WriteLine("This is an example.");
        }
    }
}
