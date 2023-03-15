using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using System.Timers;
using CommandLine;

namespace MuFS_HomeServer
{
    class Program
    {
        
        static void Main(string[] args)
        {
            Console.WriteLine("Begin Program. Args: {0}", string.Join(", ", args));
            Parser.Default.ParseArguments<HomeServerCfgOptions>(args)
                .WithParsed(opt =>
               {
                   if(opt.HelpText)
                   {
                       Console.WriteLine(HomeServerCfg.HelpText);
                   }
               });

            while(true) {
                Thread.Sleep(5000);
            }
        }
    }
}
