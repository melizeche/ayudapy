from pipeline.compressors import SubProcessCompressor

TERSER_BINARY = "/usr/bin/terser"
#TERSER_BINARY = "/usr/bin/env terser"
TERSER_ARGUMENTS = "--compress"

class TerserCompressor(SubProcessCompressor):
    def compress_js(self, js):
        command = (TERSER_BINARY, TERSER_ARGUMENTS)
        #print(command, '=============')
        # if self.verbose:
        #     command += " --verbose"
        return self.execute_command(command, js)
