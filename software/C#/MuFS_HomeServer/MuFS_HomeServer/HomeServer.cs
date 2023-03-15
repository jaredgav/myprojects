using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using CommandLine;

namespace MuFS_HomeServer
{

    public class HomeServer
    {

    }


    /**
     * <summary>The entire config for the HomeServer describing the server itself</summary>
     */
    public class HomeServerCfg
    {
        public static String HelpText = "Help Text";
    }

    /**
     * <summary>The command line options for setting up the HomeServer</summary>
     */
    public class HomeServerCfgOptions
    {
        [Option('h', "help", Required = false, HelpText = "Displays the help text")]
        public bool HelpText { get; set; }
    }

}
