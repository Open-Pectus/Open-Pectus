# Generated from c:\Projects\Novo\Open-Pectus\openpectus\lang\grammar\pcode.g4 by ANTLR 4.9.2
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .pcodeParser import pcodeParser
else:
    from pcodeParser import pcodeParser

# This class defines a complete listener for a parse tree produced by pcodeParser.
class pcodeListener(ParseTreeListener):

    # Enter a parse tree produced by pcodeParser#program.
    def enterProgram(self, ctx:pcodeParser.ProgramContext):
        pass

    # Exit a parse tree produced by pcodeParser#program.
    def exitProgram(self, ctx:pcodeParser.ProgramContext):
        pass


    # Enter a parse tree produced by pcodeParser#instruction.
    def enterInstruction(self, ctx:pcodeParser.InstructionContext):
        pass

    # Exit a parse tree produced by pcodeParser#instruction.
    def exitInstruction(self, ctx:pcodeParser.InstructionContext):
        pass


    # Enter a parse tree produced by pcodeParser#builtin_command.
    def enterBuiltin_command(self, ctx:pcodeParser.Builtin_commandContext):
        pass

    # Exit a parse tree produced by pcodeParser#builtin_command.
    def exitBuiltin_command(self, ctx:pcodeParser.Builtin_commandContext):
        pass


    # Enter a parse tree produced by pcodeParser#block.
    def enterBlock(self, ctx:pcodeParser.BlockContext):
        pass

    # Exit a parse tree produced by pcodeParser#block.
    def exitBlock(self, ctx:pcodeParser.BlockContext):
        pass


    # Enter a parse tree produced by pcodeParser#block_name.
    def enterBlock_name(self, ctx:pcodeParser.Block_nameContext):
        pass

    # Exit a parse tree produced by pcodeParser#block_name.
    def exitBlock_name(self, ctx:pcodeParser.Block_nameContext):
        pass


    # Enter a parse tree produced by pcodeParser#end_block.
    def enterEnd_block(self, ctx:pcodeParser.End_blockContext):
        pass

    # Exit a parse tree produced by pcodeParser#end_block.
    def exitEnd_block(self, ctx:pcodeParser.End_blockContext):
        pass


    # Enter a parse tree produced by pcodeParser#end_blocks.
    def enterEnd_blocks(self, ctx:pcodeParser.End_blocksContext):
        pass

    # Exit a parse tree produced by pcodeParser#end_blocks.
    def exitEnd_blocks(self, ctx:pcodeParser.End_blocksContext):
        pass


    # Enter a parse tree produced by pcodeParser#command.
    def enterCommand(self, ctx:pcodeParser.CommandContext):
        pass

    # Exit a parse tree produced by pcodeParser#command.
    def exitCommand(self, ctx:pcodeParser.CommandContext):
        pass


    # Enter a parse tree produced by pcodeParser#command_name.
    def enterCommand_name(self, ctx:pcodeParser.Command_nameContext):
        pass

    # Exit a parse tree produced by pcodeParser#command_name.
    def exitCommand_name(self, ctx:pcodeParser.Command_nameContext):
        pass


    # Enter a parse tree produced by pcodeParser#command_args.
    def enterCommand_args(self, ctx:pcodeParser.Command_argsContext):
        pass

    # Exit a parse tree produced by pcodeParser#command_args.
    def exitCommand_args(self, ctx:pcodeParser.Command_argsContext):
        pass


    # Enter a parse tree produced by pcodeParser#watch.
    def enterWatch(self, ctx:pcodeParser.WatchContext):
        pass

    # Exit a parse tree produced by pcodeParser#watch.
    def exitWatch(self, ctx:pcodeParser.WatchContext):
        pass


    # Enter a parse tree produced by pcodeParser#alarm.
    def enterAlarm(self, ctx:pcodeParser.AlarmContext):
        pass

    # Exit a parse tree produced by pcodeParser#alarm.
    def exitAlarm(self, ctx:pcodeParser.AlarmContext):
        pass


    # Enter a parse tree produced by pcodeParser#condition.
    def enterCondition(self, ctx:pcodeParser.ConditionContext):
        pass

    # Exit a parse tree produced by pcodeParser#condition.
    def exitCondition(self, ctx:pcodeParser.ConditionContext):
        pass


    # Enter a parse tree produced by pcodeParser#increment_rc.
    def enterIncrement_rc(self, ctx:pcodeParser.Increment_rcContext):
        pass

    # Exit a parse tree produced by pcodeParser#increment_rc.
    def exitIncrement_rc(self, ctx:pcodeParser.Increment_rcContext):
        pass


    # Enter a parse tree produced by pcodeParser#stop.
    def enterStop(self, ctx:pcodeParser.StopContext):
        pass

    # Exit a parse tree produced by pcodeParser#stop.
    def exitStop(self, ctx:pcodeParser.StopContext):
        pass


    # Enter a parse tree produced by pcodeParser#pause.
    def enterPause(self, ctx:pcodeParser.PauseContext):
        pass

    # Exit a parse tree produced by pcodeParser#pause.
    def exitPause(self, ctx:pcodeParser.PauseContext):
        pass


    # Enter a parse tree produced by pcodeParser#time.
    def enterTime(self, ctx:pcodeParser.TimeContext):
        pass

    # Exit a parse tree produced by pcodeParser#time.
    def exitTime(self, ctx:pcodeParser.TimeContext):
        pass


    # Enter a parse tree produced by pcodeParser#timeexp.
    def enterTimeexp(self, ctx:pcodeParser.TimeexpContext):
        pass

    # Exit a parse tree produced by pcodeParser#timeexp.
    def exitTimeexp(self, ctx:pcodeParser.TimeexpContext):
        pass


    # Enter a parse tree produced by pcodeParser#comment.
    def enterComment(self, ctx:pcodeParser.CommentContext):
        pass

    # Exit a parse tree produced by pcodeParser#comment.
    def exitComment(self, ctx:pcodeParser.CommentContext):
        pass


    # Enter a parse tree produced by pcodeParser#comment_text.
    def enterComment_text(self, ctx:pcodeParser.Comment_textContext):
        pass

    # Exit a parse tree produced by pcodeParser#comment_text.
    def exitComment_text(self, ctx:pcodeParser.Comment_textContext):
        pass


    # Enter a parse tree produced by pcodeParser#blank.
    def enterBlank(self, ctx:pcodeParser.BlankContext):
        pass

    # Exit a parse tree produced by pcodeParser#blank.
    def exitBlank(self, ctx:pcodeParser.BlankContext):
        pass


    # Enter a parse tree produced by pcodeParser#error.
    def enterError(self, ctx:pcodeParser.ErrorContext):
        pass

    # Exit a parse tree produced by pcodeParser#error.
    def exitError(self, ctx:pcodeParser.ErrorContext):
        pass



del pcodeParser