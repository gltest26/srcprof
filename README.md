
Overview
========

srcprof is a very simple source tree profiling (statistics analyzing tool) run on a command line.


Installation
----------------

This program consists of just two Python sources, just copy them on any directory of your liking.


Usage
----------------

The program is simple Python script, which can run on any platform with Python environment available.

Just type `srcprof.py` or `python srcprof.py` to get command line help.


Output data
----------------

It outputs file count, line count and total size of each source file type distinguished by extension (or suffix).

It also prints files with largest line counts, which can help finding most complex files in the source tree.

It can print source file distribution graph (with simple ASCII art), which implies how well the project is divided into modules.

For example, running this program on git source distribution yields following output.

	--------------------------
	         Summary
	--------------------------

	.h: files = 133, lines = 16960, size = 568827
	.c: files = 326, lines = 161450, size = 4311850
	.py: files = 15, lines = 5634, size = 200733
	total: files = 474, lines = 184044, size = 5081410

	--------------------------
	      Top 10 files
	--------------------------

	5750: g:\projects\git\compat\nedmalloc/malloc.c.h
	4873: g:\projects\git/diff.c
	4454: g:\projects\git\builtin/apply.c
	4369: g:\projects\git\compat\regex/regexec.c
	3884: g:\projects\git\compat\regex/regcomp.c
	3461: g:\projects\git/fast-import.c
	3183: g:\projects\git/git-p4.py
	2843: g:\projects\git/sha1_file.c
	2642: g:\projects\git\builtin/blame.c

	--------------------------
	      Distribution
	--------------------------

	    1-    1 0  :
	    2-    1 0  :
	    2-    3 0  :
	    4-    4 0  :
	    5-    7 8  :**************************************
	    8-   10 13 :********************************************
	   11-   15 13 :********************************************
	   16-   21 25 :*****************************************************
	   22-   31 30 :*******************************************************
	   32-   44 28 :******************************************************
	   45-   63 31 :*******************************************************
	   64-   89 43 :************************************************************
	   90-  127 35 :*********************************************************
	  128-  180 37 :**********************************************************
	  181-  255 32 :********************************************************
	  256-  361 41 :***********************************************************
	  362-  511 33 :********************************************************
	  512-  723 28 :******************************************************
	  724- 1023 21 :**************************************************
	 1024- 1447 23 :****************************************************
	 1448- 2047 14 :*********************************************
	 2048- 2895 6  :***********************************
	 2896- 4095 3  :**************************
	 4096- 5791 4  :******************************
	 5792- 8191 0  :
	 8192-11584 0  :
	11585-16383 0  :
	16384-23169 0  :
	23170-32767 0  :


Options
--------------

The program has some option switches. The list of available options is viewed by running the program without arguments.

	usage: srcprof.py [flags] path

	The source profiler program.

	It lists up all files in a directory tree and sum up line counts
	for making statistics analysis.

	The flags can be combination of the following:

	    +v      Enable verbose flag
	    -v      Disable verbose flag
	    +l      Enable listing of processed files.
	    -l      Disable listing of processed files.
	    +z      Enable reading sources inside zipfiles.
	    -z      Disable reading sources inside zipfiles.
	    +e ext  Add extension to search criteria
	    -e ext  Remove extension from search criteria
	    +i dir  Add directory to ignore list
	    -i dir  Remove directory from ignore list
	    +s      Enable Summary section (default)
	    -s      Disable Summary section
	    -r n    Enable ranking of file line count for top n files.
	            Set n to 0 to disable ranking. (default 10)
	    +d      Enable distribution graph (default)
	    -d      Disable distribution graph
	    -E enc  Set Zipfile entry file encoding to enc. (default CP932)
	    +h      Enable HTML output
	    -h      Disable HTML output (default)


	Default ignoredirs:
	set(['.hg', '.svn'])
	Default extensions:
	set(['.h', '.cs', '.rc', '.rb', '.c', '.rci', '.dlg', '.py', '.cpp', '.dpr', '.p
	as'])


Origin
------------

During certain project development, I just wondered which source file is the most complex one in the whole project (thus probably be worth refactoring). I also wanted to know the trend of the whole project.
Instead of searching for countless statistical analysis tools, I just wrote one I needed.
