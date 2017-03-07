from __future__ import print_function

try:
    import gdb
except ImportError:
    print("Not running inside of GDB, exiting...")
    import sys
    sys.exit()

from libheap.printutils import print_header
from libheap.printutils import print_error

from libheap.ptmalloc.ptmalloc import ptmalloc

from libheap.ptmalloc.malloc_state import malloc_state

from libheap.debugger.pygdbpython import get_inferior
from libheap.debugger.pygdbpython import read_variable


class heap(gdb.Command):
    """libheap command help listing"""

    def __init__(self):
        super(heap, self).__init__("heap", gdb.COMMAND_USER, gdb.COMPLETE_NONE)

    def invoke(self, arg, from_tty):
        if arg.find("-h") != -1:
            # print_header("heap ", end="")
            # print("Options:", end="\n\n")
            # print_header("{:<15}".format("-a 0x1234"))
            # print("Specify an arena address")
            print_header("{:<15}".format("heapls"))
            print("Print a flat listing of all chunks in an arena")
            print_header("{:<15}".format("fastbins [#]"))
            print("Print all fast bins, or only a single fast bin")
            print_header("{:<15}".format("smallbins [#]"))
            print("Print all small bins, or only a single small bin")
            print_header("{:<15}".format("freebins"))
            print("Print compact bin listing (only free chunks)")
            print_header("{:<15}".format("heaplsc"))
            print("Print compact arena listing (all chunks)")
            print_header("{:<15}".format("mstats"), end="")
            print("Print memory alloc statistics similar to malloc_stats(3)")
            # print_header("{:<22}".format("print_bin_layout [#]"), end="")
            # print("Print the layout of a particular free bin")
            return

        ptm = ptmalloc()
        inferior = get_inferior()

        if ptm.SIZE_SZ == 0:
            ptm.set_globals()

        # XXX: from old heap command, replace
        main_arena = read_variable("main_arena")
        # XXX: add arena address guessing via offset without symbols
        arena_address = main_arena.address
        ar_ptr = malloc_state(arena_address, inferior=inferior)

        # XXX: add arena address passing via arg (-a)
        if (len(arg) == 0) and (ar_ptr.next == 0):
            # struct malloc_state may be invalid size (wrong glibc version)
            print_error("No arenas could be found at {:#x}".format(
                        ar_ptr.address))
            return

        print("Arena(s) found:", end="\n")
        print("  arena @ ", end="")
        print_header("{:#x}".format(int(ar_ptr.address)), end="\n")

        if ar_ptr.address != ar_ptr.next:
            # we have more than one arena

            curr_arena = malloc_state(ar_ptr.next, inferior=inferior)

            while (ar_ptr.address != curr_arena.address):
                print("  arena @ ", end="")
                print_header("{:#x}".format(int(curr_arena.address)), end="\n")
                curr_arena = malloc_state(curr_arena.next, inferior=inferior)

                if curr_arena.address == 0:
                    print_error("No arenas could be correctly found.")
                    break  # breaking infinite loop
