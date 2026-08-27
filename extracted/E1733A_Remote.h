/*########################################################################################
#
# Copyright (c) 2020, Keysight Technologies, Inc
#_________________________________________________________________________________________
#
# File			: E1733A_Remote.h
#
# Project		: Remote Control for E1733A Calibration Software
#
# Date			: 24 Sep. 2020 (for v1.14)
#_________________________________________________________________________________________
#
# Description : This file contains constants for controlling the E1733A software with
#               Windows Messaging. It is a shared file with the E1733A software.
#
/*######################################################################################*/

/*######################################################################################*/
// NOTE: this is a preliminary revision for evaluation purposes.
// Definitions of all constants and types are subject to change in succeeding revisions.
/*######################################################################################*/

/*## Modification History ##############################################################*/
// as issued for E1733A revision 1.12a1, last update 2017.4.18
// update 2017.5.31: *_AUTOTIMER_ITEMTEXT is removed, *_CI_APPLY and *_E1735ASN_CHOOSING et. al. are added.
// update 2018.4.26: for dual axes, E1733A_CI_LDASETUP_LDA*_* are changed to E1733A_CI_XDASETUP_XDA*_*, to support more measurement types
// update 2020.9.3: added 5 constants for the current point: cycle, axis, direction, index and target position

// About dual axes
// When the program goes into dual axes measurement, the current program is terminated
// and two new instances are initiated. The remote parameter is passed to them too,
// User should then search for their handles again, whose window title has a title of
// "(Axis:1)" or "(Axis:2)" respectively. After these windows are all closed, the program
// will be restored with a new window, user should search for its handle again.

#pragma pack(push, enter_include_E1736ACore)
#pragma pack(1) 

// type definition of the first parameter of windows message
typedef union { 
	LONG AsWParam;				// basic parameter of the message
	struct { 
		unsigned char Code;		// indicating type of action, predefined as E1733A_CC_xxxx
		unsigned char Index;	// target or sub-type of action, predefnied as E1733A_CI_xxxx
		unsigned short Num;		// index number of items or run number of the error data
	} Command;
} TWParam;

// type definition of the second parameter of windows message, not used for most of messages
typedef union {
	LONG AsLParam;			// additional parameter of the message
	struct { 
		signed short X;		// X position or width
		signed short Y;		// Y position or height
	} XY;
	LONG Pos;				// position number of the error data
} TLParam;

// type definition of the result of message
typedef union {
	LONG Integer;		// result is integer, boolean, or index defined by E1733A_RC_xxxx 
	float Single;		// result is single precision float number
} TIntFloat;

#pragma pack(pop, enter_include_E1736ACore)

// command line parameter, followed by a text as the user defined name for E1733A Automation
#define E1733A_CS_REMOTENAME "/RemoteName="

// used in SendMessage routine
#define E1733A_WM_REMOTECOMMAND 0x0500

// return codes
#define E1733A_RC_SUCCESSFUL 0
#define E1733A_RC_INVALIDCOMMAND 1
#define E1733A_RC_UNEXPECTEDERROR 2
#define E1733A_RC_INVALIDPARAMETER 3
#define E1733A_RC_INDEXOUTOFRANGE 4
#define E1733A_RC_NULLPOINTER 5
#define E1733A_RC_STRINGNOTEXISTS 6
#define E1733A_RC_NOTENOUGHSPACE 7
#define E1733A_RC_SIZENOTMATCH 8
#define E1733A_RC_CANNOTOPENFILE 9
#define E1733A_RC_ALREADYOPENED 10
#define E1733A_RC_NOSUCHDIRECTORY 11
#define E1733A_RC_FAILEDTOSAVEFILE 12
#define E1733A_RC_WRITETOREADONLY 13
#define E1733A_RC_FUNCTIONDISABLED 14
#define E1733A_RC_INDEXISDISABLED 15
#define E1733A_RC_INVALIDINDEX 16
#define E1733A_RC_FILENOTFOUND 17
#define E1733A_RC_CANNOTACCESSFILE 18
#define E1733A_RC_STRINGTRUNCATED 19
#define E1733A_RC_FAILEDTOWRITE 20

// change status of E1733A software
#define E1733A_CC_SETE1733ASTATUS 10
#define E1733A_CI_ENABLED 0
#define E1733A_CI_DISABLED 1
#define E1733A_CI_SHOW 2
#define E1733A_CI_HIDE 3
#define E1733A_CI_MAXIMIZE 4
#define E1733A_CI_MINIMIZE 5
#define E1733A_CI_RESTORE 6
#define E1733A_CI_RESIZE 7      // use second parameter, LParam, to define the size of window in pixel, X for width, Y for height
#define E1733A_CI_MOVETO 8      // use second parameter, LParam, to move to screen position (X,Y) in pixel, X=0 and Y=0 to for top-left corner of screen
#define E1733A_CI_MOVESETUP 9

// change display style
#define E1733A_CC_CHANGEDISPLAY 11
#define E1733A_CI_NORMALDISPLAY 0
#define E1733A_CI_ENLARGENUMERIC 1
#define E1733A_CI_ENLARGEGRAPH 2

// change numeric display
#define E1733A_CC_SELECTUPPERDISP 20
#define E1733A_CC_SELECTLOWERDISP 21
#define E1733A_CI_LASER 0
#define E1733A_CI_ERROR 2
#define E1733A_CI_TARGET 3
#define E1733A_CI_ENCODER 4
#define E1733A_CI_ANGLE 6
#define E1733A_CI_TIME 7
#define E1733A_CI_VELOCITY 8
#define E1733A_CI_STATION 9

// for buttons on numeric display area
#define E1733A_CC_CHANGENUMERIC 22
#define E1733A_CI_INCUPPER 0
#define E1733A_CI_DECUPPER 1
#define E1733A_CI_INCLOWER 2
#define E1733A_CI_DECLOWER 3
#define E1733A_CI_POSUPPER 4
#define E1733A_CI_NEGUPPER 5
#define E1733A_CI_POSLOWER 6
#define E1733A_CI_NEGLOWER 7

// for [Graph] button
#define E1733A_CC_SHOWGRAPH 30
#define E1733A_CI_GRAALL 0
#define E1733A_CI_GRAAXIS1 1
#define E1733A_CI_GRAAXIS2 2
#define E1733A_CI_GRAAXIS3 3
#define E1733A_CI_GRAAXIS4 4
#define E1733A_CI_GRAAXIS5 5
#define E1733A_CI_GRAAXIS6 6
#define E1733A_CI_GRAAXIS7 7
#define E1733A_CI_GRAAXIS8 8
#define E1733A_CI_GRAPOS 10
#define E1733A_CI_GRAVEL 11
#define E1733A_CI_GRAACC 12
#define E1733A_CI_GRAFFT 13

// for [Data] button
#define E1733A_CC_SHOWRAWDATATABLE 31
#define E1733A_CI_DATALL 0
#define E1733A_CI_DATAXIS1 1
#define E1733A_CI_DATAXIS2 2
#define E1733A_CI_DATAXIS3 3
#define E1733A_CI_DATAXIS4 4
#define E1733A_CI_DATAXIS5 5
#define E1733A_CI_DATAXIS6 6
#define E1733A_CI_DATAXIS7 7
#define E1733A_CI_DATAXIS8 8

// for [Comp] button
#define E1733A_CC_SHOWCOMPENSATION 32
#define E1733A_CI_COMPALL 0
#define E1733A_CI_COMPAXIS1 1
#define E1733A_CI_COMPAXIS2 2

// for [Env] button
#define E1733A_CC_SHOWENVIRONMENT 33
#define E1733A_CI_STAT 0
#define E1733A_CI_AT 1
#define E1733A_CI_AP 2
#define E1733A_CI_RH 3
#define E1733A_CI_MAT 4

// for buttons on main window, to enter new measurement with default setup
#define E1733A_CC_NEW 40
#define E1733A_CI_LINEAR 0
#define E1733A_CI_ANGULAR 1
#define E1733A_CI_STRAIGHTNESS 2
#define E1733A_CI_SQUARENESS 3
#define E1733A_CI_PARALLELISM 4
#define E1733A_CI_ROTARY 5
#define E1733A_CI_WAYSTRAIGHTNESS 6
#define E1733A_CI_FLATNESS 7
#define E1733A_CI_DIAGONAL 8
#define E1733A_CI_LINTIMEBASE 9
#define E1733A_CI_ANGTIMEBASE 10
#define E1733A_CI_STRTIMEBASE 11
#define E1733A_CI_SINGLEAXIS 13
#define E1733A_CI_DUALAXIS 14

// for [Open] button
// file name is send to E1733A via shared memory file, WParam.Num=length of string
// user should open a shared memory file and make sure its size enough
// check demo program for more information
#define E1733A_CC_OPEN 50
#define E1733A_CI_SETUPONLY 0
#define E1733A_CI_SETUPDATA 1
#define E1733A_CI_INFOONLY 2	// only in data window
#define E1733A_CI_MERGEDATA 3	// only in data window, just for linear, angular, straightness and Rotary
#define E1733A_CI_COMBINED 4	// only in data window, just for parallelism/squareness, use comma to split two file names
#define E1733A_CI_COMBINEDPAR 5	// only in main window, for parallelism, use comma to split two file names
#define E1733A_CI_COMBINEDSQU 6	// only in main window, for squareness, use comma to split two file names

// for [Setup] button
#define E1733A_CC_SETUP 51
#define E1733A_CI_PROGRAM 0		// only in main window
#define E1733A_CI_SYSTEM 1		// this and below are only in data window
#define E1733A_CI_ENVIRONMENT 2
#define E1733A_CI_MEASUREMENT 3
#define E1733A_CI_ANALYSIS 5
#define E1733A_CI_MACHINEINFO 6
#define E1733A_CI_ISOINFO 7
#define E1733A_CI_SETUPOK 9         // press [OK] button on setup form
#define E1733A_CI_SETUPCANCEL 10    // press [Cancel] button on setup form
#define E1733A_CI_TOGGLELASER 11    // toggle the sign of the laser value
#define E1733A_CI_CALISTEP1 12      // do step 1 of rotary table calibration
#define E1733A_CI_CALISTEP2 13      // do step 2 of rotary table calibration
#define E1733A_CI_CALISTEP3 14      // do step 3 of rotary table calibration
#define E1733A_CI_APPLYCALI 15      // apply user calibration to change the factor
#define E1733A_CI_APPLY 16          // apply user defined target positions
#define E1733A_CI_IMPORT 17         // import settings from another instance of E1733A of dual axis

// for [Reset] button, only in data window
#define E1733A_CC_RESET 52			// result: E1733A_RC_xxxx

// for [Start]/[Continue] button, only in data window
#define E1733A_CC_START 53			// result: E1733A_RC_xxxx

// for [Record] button, only in data window
#define E1733A_CC_RECORD 54			// result: E1733A_RC_xxxx

// [Stop] button, only in data window
#define E1733A_CC_STOP 55			// result: E1733A_RC_xxxx

// for [Erase] button, only in data window, no warning
#define E1733A_CC_ERASE 56			// result: E1733A_RC_xxxx
#define E1733A_CI_ALL 0
#define E1733A_CI_RUN 1
#define E1733A_CI_ONE 2
#define E1733A_CI_MER 3

// for [Save] button, only in data window
// same as that of [Open] button, shared memory file is used to send the file name
// if the file already exists, it will be overwritten without any warning
#define E1733A_CC_SAVE 57			// result: E1733A_RC_xxxx
#define E1733A_CI_STEUPDATA 0
#define E1733A_CI_RAWDATA_TXT 1
#define E1733A_CI_RAWDATA_CSV 2
#define E1733A_CI_RAWDATA_POS 3
#define E1733A_CI_RAWDATA_RUN 4
#define E1733A_CI_COMPTABLE_TXT 5
#define E1733A_CI_COMPTABLE_CSV 6
#define E1733A_CI_COMPTABLE_POS 7
#define E1733A_CI_COMPTABLE_RUN 8
#define E1733A_CI_ENVDATA_TXT 9
#define E1733A_CI_ENVDATA_CSV 10

// for [Print] button, only in data window
#define E1733A_CC_PRINT 58			// result: E1733A_RC_xxxx
#define E1733A_CI_REPORT 0
#define E1733A_CI_RAWBYPOS 1
#define E1733A_CI_RAWBYRUN 2
#define E1733A_CI_ISO1988 3
#define E1733A_CI_ISO1997 4
#define E1733A_CI_ISO2006 5
#define E1733A_CI_ISO2014 7
#define E1733A_CI_GB2000 6

// for [Exit] button
#define E1733A_CC_EXIT 59			// result: E1733A_RC_xxxx
#define E1733A_CI_MAIN 0			// exit main window, this will close the program
#define E1733A_CI_DATA 1			// exit data window and return to main window
#define E1733A_CI_SETUP 2			// exit setup window, all setup changes will be accepted

// get current running status of E1733A
#define E1733A_CC_READSTATUS 60
#define E1733A_CI_ACTIVEWINDOW 0		// result: 0=main, 1=data, 2=setup
#define E1733A_CI_5519ABREADY 1			// result: 0=false, 1=true
#define E1733A_CI_E1735AREADY 3			// result: 0=false, 1=true
#define E1733A_CI_E1735ACOUNT 5			// result: number of connected E1735A
#define E1733A_CI_E1736AREADY 9			// result: 0=false, 1=true
#define E1733A_CI_E1736ACOUNT 10		// result: number of connected E1736A
#define E1733A_CI_E1737ACOUNT 12		// result: number of connected E1737A
#define E1733A_CI_E1738ACOUNT 16		// result: number of connected E1738A
#define E1733A_CI_55290BREADY 18		// result: 0=false, 1=true
#define E1733A_CI_BEAMSTRENGTH 21		// result: beam strength in %, 0=None, 100=full
#define E1733A_CI_MEASURESETUPOK 23		// result: 0=false, 1=true
#define E1733A_CI_HASERRORMESSAGE 24	// result: 0=false, 1=true
#define E1733A_CI_ERRORMESSAGE 25		// result: string is returned via memory shared file, WParam.Num = buffer size 
#define E1733A_CI_ISMEASURING 26		// result: 0=false, 1=true
#define E1733A_CI_SAMPLECOUNT 27		// result: number of samples that has been recorded
#define E1733A_CI_ACCOMPLISHED 28		// result: 0=false, 1=true
#define E1733A_CI_UPPERDISPLAY 30		// result: upper display value as float (4-byte), NAN when error
#define E1733A_CI_LOWERDISPLAY 31		// result: lower display value as float (4-byte)
#define E1733A_CI_UPPERSELECTION 32		// result: CI_xxxx that are defined for E1733A_CC_SELECTUPPERDISP, Laser=0, Error=2, Target=3, Encoder=4, Angle=6, Time=7, Velocity=8, Station=9
#define E1733A_CI_LOWERSELECTION 33		// result: same as E1733A_CI_UPPERSELECTION
#define E1733A_CI_UPPERUNITS 34			// result: string is returned via memory shared file, WParam.Num = buffer size
#define E1733A_CI_LOWERUNITS 35			// result: same as CI_UpperUnits
#define E1733A_CI_UPPERSTRING 36		// result: E1733A_RC_xxxx, and shared memory file: upper display value as string, or error message if there is any
#define E1733A_CI_LOWERSTRING 37		// result: E1733A_RC_xxxx, and shared memory file: lower display value as string
#define E1733A_CI_CURRENTCYCLE 38;     	// result: 1=first cycle, ...
#define E1733A_CI_CURRENTAXIS 39;      	// result: 0=none, 1=first axis, ...
#define E1733A_CI_NEXTDIRECTION 40;    	// result: 1=forward, -1=backward
#define E1733A_CI_NEXTINDEX 41;        	// result: 1=first position, ...
#define E1733A_CI_NEXTTARGET 42;       	// result: convert the low 4 bytes of the return value into float

// read error data
// assign run number to WParam.Num, position number to LParam.Pos
// the value is returned as result of the message, in 4-byte, transfer it to float
// if the functin fails, for example, index out of range, NAN will be returned
#define E1733A_CC_READERRORDATA 62		// result: E1733A_RC_xxxx
#define E1733A_CI_ERRAXIS1 1
#define E1733A_CI_ERRAXIS2 2
#define E1733A_CI_ERRAXIS3 3
#define E1733A_CI_ERRAXIS4 4
#define E1733A_CI_ERRAXIS5 5
#define E1733A_CI_ERRAXIS6 6
#define E1733A_CI_ERRAXIS7 7
#define E1733A_CI_ERRAXIS8 8

// access setup values of E1733A
// all values are read and written as a string, send and get via memory share file, see demo program for how to use it
// message result is defnied by E1733A_RC_xxxx
#define E1733A_CC_READSETUPVALUE 64				// read a setup value from E1733A program
#define E1733A_CC_WRITESETUPVALUE 65			// write a setup value to E1733A program
// All values are read and written as string (ANSI coding), via shared memory file
// Those that have a postfix of _COMPRISE, are for a list of options, represented by a serial of characters, for example, "10100", each one indicates one option, 0=unchecked, 1=checked, the length of string must match the number of options
// Those that have a postfix of _CHOOSING, are for boolean type and limited selections, use a number (in string form), for example, "3", to specify the selection, some options may be not available in all cases
// Those that have a postfix of _ITEMTEXT or _ITEMUNIT, are for string type, or integer and float value that have no unit, for example, "John Smith" for E1733A_CI_INFSETUP_OPERATOR_ITEMTEXT, "5" for E1733A_CI_MEASETUP_CYCLES_ITEMTEXT
// User can read back the value to check if the value is properly assigned.
/*		DATA ANALYSIS	*/
#define E1733A_CI_ANASETUP_ANAGRAPH_COMPRISE 68         // [Data Analysis] -> "Graphic Analysis"; 0: Forward Data Runs, 1: Forward Mean, 2: Forward +/-n sigma, 3: Reverse Data Runs, 4: Reverse Mean, 5: Reverse +/-n sigma, 6: Combined Mean, 7: Combined +/-n sigma, 8: Remove Raw Offset, 9: Backlash / pt., 
#define E1733A_CI_ANASETUP_ANAMOD_CHOOSING 80           // [Data Analysis] -> "Modified"; 0: No, 1: Yes, 
#define E1733A_CI_ANASETUP_ANANUM_COMPRISE 71           // [Data Analysis] -> "Numerical Analysis"; 0: Accuracy, 1: Repeatability, 2: Mean Reversal Error, 3: Sys. Dev. Pos., 4: Mean Bidir. Pos. Dev., 5: Raw Accuracy, 6: Raw Repeatability, 7: Max Reversal Error, 8: 6 Sigma (total pop.), 9: Slope, 
#define E1733A_CI_ANASETUP_ANASIGMA_ITEMTEXT 74         // [Data Analysis] -> "Coverage Factor (Sigma)"; 
#define E1733A_CI_ANASETUP_ANASLOPE_CHOOSING 72         // [Data Analysis] -> "Slope"; 0: Least Squares, 1: End Points, 
#define E1733A_CI_ANASETUP_COMPZERO_ITEMTEXT 70         // [Data Analysis] -> "Machine Zero Point"; 
#define E1733A_CI_ANASETUP_FLAMETHOD_CHOOSING 73        // [Data Analysis] -> "Analyze Data"; 0: Moody, 
#define E1733A_CI_ANASETUP_PRNCOPIES_ITEMTEXT 78        // [Data Analysis] -> "Copies"; 
#define E1733A_CI_ANASETUP_PRNENVSEL_CHOOSING 76        // [Data Analysis] -> "Environmental Data"; 0: Max/Min/Mean, 1: Start/End, 
#define E1733A_CI_ANASETUP_PRNNAME_CHOOSING 77          // [Data Analysis] -> "Printer"; 0,1,2...: Index of installed printers,
#define E1733A_CI_ANASETUP_PRNORIENT_CHOOSING 79        // [Data Analysis] -> "Orientation"; 0: Portrait, 1: Landscape, 
#define E1733A_CI_ANASETUP_PRNSHOWSEL_COMPRISE 75       // [Data Analysis] -> "Print"; 0: Show Legend, 1: Show Machine Info, 2: Numerical Analysis, 3: Environmental Data,
#define E1733A_CI_ANASETUP_PRNMARGIN_CHOOSING 152       // [Data Analysis] -> "Extra Margin"; 0: None, 1: Left, 2: Top; 3: Right; 4: Bottom
#define E1733A_CI_ANASETUP_STANDARD_CHOOSING 81         // [Data Analysis] -> "Standards"; 0: NMTBA w/o Offset, 1: NMTBA, 2: ANSI B5.54/B5.57, 3: VDI 3441/2617, 4: BSI 3800, 5: JIS B6330, 6: ISO 230-2 1988, 7: ISO 230-2 1997, 8: GB10931-89, 9: GB/T 17421.2-2000, 10: User, 11: ISO 230-2 2006, 12: ISO 230-2 2014,
#define E1733A_CI_ANASETUP_TBDATAPNT_CHOOSING 69        // [Data Analysis] -> "Data Point"; 0: No, 1: Yes, 
/*		COMPENSATION TABLE	*/
#define E1733A_CI_CMPSETUP_COMPABS_CHOOSING 126         // [Compensation Table] -> "Error Sign Convention"; 0: Algebraic, 1: Calibrator, 
#define E1733A_CI_CMPSETUP_COMPCALC_CHOOSING 127        // [Compensation Table] -> "Compensation Values"; 0: Absolute, 1: Incremental, 
#define E1733A_CI_CMPSETUP_COMPDIR_CHOOSING 129         // [Compensation Table] -> "Direction"; 0: Combined, 1: Forward/Reverse, 
#define E1733A_CI_CMPSETUP_COMPEND_ITEMTEXT 133         // [Compensation Table] -> "End Position"; 
#define E1733A_CI_CMPSETUP_COMPINTVL_ITEMTEXT 134       // [Compensation Table] -> "Interval"; 
#define E1733A_CI_CMPSETUP_COMPPROG_ITEMTEXT 120        // [Compensation Table] -> "Download"; 
#define E1733A_CI_CMPSETUP_COMPSEL_CHOOSING 131         // [Compensation Table] -> "Target Position"; 0: Target List , 1: Interpolate, 
#define E1733A_CI_CMPSETUP_COMPSIGN_CHOOSING 128        // [Compensation Table] -> "Type"; 0: Correction, 1: Error, 
#define E1733A_CI_CMPSETUP_COMPSTART_ITEMTEXT 132       // [Compensation Table] -> "Start Position"; 
#define E1733A_CI_CMPSETUP_MACHUNIT_ITEMTEXT 130        // [Compensation Table] -> "Machine Units"; 
/*		DATA DISPLAY	*/
#define E1733A_CI_DATSETUP_ERRORSIGN_CHOOSING 121       // [Data Display] -> "ErrorSign"; 0: +X, 1: -X, 
#define E1733A_CI_DATSETUP_FIRSTROW_ITEMTEXT 122        // [Data Display] -> "Goto Row"; 
#define E1733A_CI_DATSETUP_FLAGRASEL_CHOOSING 125       // [Data Display] -> "3D"; 0: No, 1: Yes, 
#define E1733A_CI_DATSETUP_GRIDLINES_CHOOSING 124       // [Data Display] -> "Grid Lines"; 0: No, 1: Yes, 
#define E1733A_CI_DATSETUP_LEGEND_CHOOSING 115          // [Data Display] -> "Legend"; 0: No, 1: Yes, 
#define E1733A_CI_DATSETUP_LIMITLINE_ITEMTEXT 116       // [Data Display] -> "Limit Lines"; 
#define E1733A_CI_DATSETUP_LIMITSEL_CHOOSING 117        // [Data Display] -> "Limit Lines"; 0: No, 1: Yes, 
#define E1733A_CI_DATSETUP_TARINROW_CHOOSING 123        // [Data Display] -> "Targets in Row"; 0: No, 1: Yes, 
#define E1733A_CI_DATSETUP_USERSCALE_ITEMTEXT 119       // [Data Display] -> "User Scale"; 
#define E1733A_CI_DATSETUP_USERSEL_CHOOSING 118         // [Data Display] -> "User Scale"; 0: No, 1: Yes, 
/*		ENVIRONMENTAL COMP	*/
#define E1733A_CI_ENVSETUP_AIRPRES_ITEMTEXT 9           // [Environmental Compensation] -> "Air Pressure"; 
#define E1733A_CI_ENVSETUP_AIRTEMP_ITEMTEXT 10          // [Environmental Compensation] -> "Air Temperature"; 
#define E1733A_CI_ENVSETUP_ENVUNITSEL_CHOOSING 8        // [Environmental Compensation] -> "Environmental Units"; 0: Metric (C; mmHg), 1: English (F; inHg), 2: SI (C; kPa), 
#define E1733A_CI_ENVSETUP_MANUALRH_CHOOSING 12         // [Environmental Compensation] -> "Manual"; 0: No, 1: Yes, 
#define E1733A_CI_ENVSETUP_MATTEMP1_ITEMTEXT 13         // [Environmental Compensation] -> "Material Temp. 1"; 
#define E1733A_CI_ENVSETUP_MATTEMP2_ITEMTEXT 14         // [Environmental Compensation] -> "Material Temp. 2"; 
#define E1733A_CI_ENVSETUP_MATTEMP3_ITEMTEXT 15         // [Environmental Compensation] -> "Material Temp. 3"; 
#define E1733A_CI_ENVSETUP_RELHUMI_ITEMTEXT 11          // [Environmental Compensation] -> "Relative Humidity";
#define E1733A_CI_ENVSETUP_AIRUPDATE_ItemText 160;      // [Environmental Compensation] -> "Air Sensor -> Update Method"; 1: Manual, 2: Import; just for dual axis without sensor
#define E1733A_CI_ENVSETUP_MATUPDATE_ItemText 161;      // [Environmental Compensation] -> "Material Sensor -> Update Method"; 1: Manual, 2: Import; just for dual axis without sensor
/*		MACHINE INFORMATION	*/
#define E1733A_CI_INFSETUP_ASSETNO_ITEMTEXT 83          // [Machine Information] -> "Asset No.";
#define E1733A_CI_INFSETUP_COMMENTS_ITEMTEXT 82         // [Machine Information] -> "Comments";
#define E1733A_CI_INFSETUP_LOCATION_ITEMTEXT 88         // [Machine Information] -> "Location";
#define E1733A_CI_INFSETUP_MACHMODEL_ITEMTEXT 84        // [Machine Information] -> "Machine Model No.";
#define E1733A_CI_INFSETUP_MACHNAME_ITEMTEXT 87         // [Machine Information] -> "Machine Name";
#define E1733A_CI_INFSETUP_MACHSN_ITEMTEXT 85           // [Machine Information] -> "Machine Serial No.";
#define E1733A_CI_INFSETUP_MACHTYPE_ITEMTEXT 86         // [Machine Information] -> "Machine Type";
#define E1733A_CI_INFSETUP_DATETEST_ITEMTEXT 147		// [Machine Information] -> "Date of Test";
/*		ISO INFORMATION	*/
#define E1733A_CI_INFSETUP_OPERATOR_ITEMTEXT 89         // [ISO Information] -> "Name of Inspector";
#define E1733A_CI_ISOSETUP_ALIGNERR_ITEMTEXT 111        // [ISO Information] -> "Alignment; Assumed";
#define E1733A_CI_ISOSETUP_ATSEN_ITEMTEXT 106           // [ISO Information] -> "Air Sensor"; 
#define E1733A_CI_ISOSETUP_CALMEADEV_CHOOSING 109       // [ISO Information] -> "Calibrated Measuring Device"; 0: No, 1: Yes, 
#define E1733A_CI_ISOSETUP_COEFSCALE_ITEMTEXT 95        // [ISO Information] -> "Coefficient of Thermal Expansion of Scale"; 
#define E1733A_CI_ISOSETUP_COMPUSED_ITEMTEXT 92         // [ISO Information] -> "Compensation Used"; 
#define E1733A_CI_ISOSETUP_DIFF20CMAX_ITEMTEXT 112      // [ISO Information] -> "Difference to 20C; Maximum"; 
#define E1733A_CI_ISOSETUP_DWELLTIME_ITEMTEXT 91        // [ISO Information] -> "Dwell Time at Each Target Position"; 
#define E1733A_CI_ISOSETUP_ENVVARERR_ITEMTEXT 113       // [ISO Information] -> "Environmental Variation"; 
#define E1733A_CI_ISOSETUP_ERRORRANGE_ITEMTEXT 108      // [ISO Information] -> "Error Range" (value);
#define E1733A_CI_ISOSETUP_ERRORRANGE_ITEMUNIT 148      // [ISO Information] -> "Error Range" (unit);
#define E1733A_CI_ISOSETUP_FEEDRATE_ITEMTEXT 94         // [ISO Information] -> "Feed Rate";
#define E1733A_CI_ISOSETUP_MATSEN1_ITEMTEXT 104         // [ISO Information] -> "Material Sensor #1"; 
#define E1733A_CI_ISOSETUP_MATSEN2_ITEMTEXT 105         // [ISO Information] -> "Material Sensor #2"; 
#define E1733A_CI_ISOSETUP_MATSEN3_ITEMTEXT 107         // [ISO Information] -> "Material Sensor #3"; 
#define E1733A_CI_ISOSETUP_MATTEMPDEV_ITEMTEXT 114      // [ISO Information] -> "(Material Sensor) Deviation; Maximum"; 
#define E1733A_CI_ISOSETUP_MEAINST_ITEMTEXT 96          // [ISO Information] -> "Measuring Instrument and Serial No."; 
#define E1733A_CI_ISOSETUP_NDECORR_CHOOSING 90          // [ISO Information] -> "NDE Correction (yes or no)"; 0: No, 1: Yes, 
#define E1733A_CI_ISOSETUP_PIECEX_ITEMTEXT 101          // [ISO Information] -> "Offset to Workpiece Reference (X/Y/Z)"; 
#define E1733A_CI_ISOSETUP_PIECEY_ITEMTEXT 102          // [ISO Information] -> "PieceY"; 
#define E1733A_CI_ISOSETUP_PIECEZ_ITEMTEXT 103          // [ISO Information] -> "PieceZ"; 
#define E1733A_CI_ISOSETUP_POSAXES_ITEMTEXT 97          // [ISO Information] -> "Position of axes not under test"; 
#define E1733A_CI_ISOSETUP_TOOLX_ITEMTEXT 98            // [ISO Information] -> "Offset to Tool Reference (X/Y/Z)"; 
#define E1733A_CI_ISOSETUP_TOOLY_ITEMTEXT 99            // [ISO Information] -> "ToolY"; 
#define E1733A_CI_ISOSETUP_TOOLZ_ITEMTEXT 100           // [ISO Information] -> "ToolZ"; 
#define E1733A_CI_ISOSETUP_TYPESCALE_ITEMTEXT 93        // [ISO Information] -> "Type of Scale"; 
#define E1733A_CI_ISOSETUP_UNCEXPCOEF_ITEMTEXT 110      // [ISO Information] -> "Uncertainty of Expansion Coefficient"; 
/*		MEASURMENT SETUP	*/
#define E1733A_CI_MEASETUP_ALLOWKBPOS_CHOOSING 42       // [Measurement Setup] -> "Keyboard Position"; 0: No, 1: Yes, 
#define E1733A_CI_MEASETUP_AQBMODE_CHOOSING 33          // [Measurement Setup] -> "Encoder"; 0: AQB, 1: Up/Down, 
#define E1733A_CI_MEASETUP_HYSTERESIS_ITEMTEXT = 162;   // [Measurement Setup] -> "Hysteresis";
#define E1733A_CI_MEASETUP_AQBRES_ITEMTEXT 31           // [Measurement Setup] -> "Encoder Resolution" (value);
#define E1733A_CI_MEASETUP_AQBRES_ITEMUNIT 139          // [Measurement Setup] -> "Encoder Resolution" (unit);
#define E1733A_CI_MEASETUP_AVERAGE_ITEMTEXT 48          // [Measurement Setup] -> "Averaging";
#define E1733A_CI_MEASETUP_AXIS_ITEMTEXT 25             // [Measurement Setup] -> "Measurement Axis";
#define E1733A_CI_MEASETUP_AUTOTITLE_CHOOSING 150		// [Measurement Setup] -> "Measurement Axis";  0: user's, 1: auto graph caption
#define E1733A_CI_MEASETUP_AXIS2_ITEMTEXT 30            // [Measurement Setup] -> "Measurement Axis" (Axis 2); 
#define E1733A_CI_MEASETUP_CYCLES_ITEMTEXT 22           // [Measurement Setup] -> "No. of Cycles"; 
#define E1733A_CI_MEASETUP_DEADPATH_ITEMTEXT 46         // [Measurement Setup] -> "Dead Path"; 
#define E1733A_CI_MEASETUP_DIASCALEX_ITEMTEXT 58        // [Measurement Setup] -> "X"; (Diagonal)
#define E1733A_CI_MEASETUP_DIASCALEY_ITEMTEXT 59        // [Measurement Setup] -> "Y"; (Diagonal)
#define E1733A_CI_MEASETUP_DIASCALEZ_ITEMTEXT 60        // [Measurement Setup] -> "Z"; (Diagonal)
#define E1733A_CI_MEASETUP_ENDPOS_ITEMTEXT 19           // [Measurement Setup] -> "End Position"; 
#define E1733A_CI_MEASETUP_ENDPOS2_ITEMTEXT 56          // [Measurement Setup] -> "End Position" (Axis 2); 
#define E1733A_CI_MEASETUP_EPTIMEOUT_ITEMTEXT 43        // [Measurement Setup] -> "End Point Time Out"; 
#define E1733A_CI_MEASETUP_ERRUNIT_CHOOSING 41          // [Measurement Setup] -> "Error Units"; 0: mm, 1: um, 2: nm, 3: inches, 4: thous, 5: uin, 6: arcdeg, 7: arcsec, 8: um/m, 9: uin/in, 
#define E1733A_CI_MEASETUP_EXPCOEF_ITEMTEXT 37          // [Measurement Setup] -> "Expans. Coeff."; 
#define E1733A_CI_MEASETUP_FLAAXISDIR_CHOOSING 29       // [Measurement Setup] -> "Direction"; 0: A->E, 1: E->A, 
#define E1733A_CI_MEASETUP_FLALENAC_ITEMTEXT 137        // [Measurement Setup] -> "AC"; 
#define E1733A_CI_MEASETUP_FLALENAG_ITEMTEXT 138        // [Measurement Setup] -> "AG"; 
#define E1733A_CI_MEASETUP_FLASTAAC_ITEMTEXT 26         // [Measurement Setup] -> "AC"; 
#define E1733A_CI_MEASETUP_FLASTAAG_ITEMTEXT 28         // [Measurement Setup] -> "AG"; 
#define E1733A_CI_MEASETUP_FOOTSPACE_ITEMTEXT 47        // [Measurement Setup] -> "Foot Spacing"; 
#define E1733A_CI_MEASETUP_INTERVAL_ITEMTEXT 17         // [Measurement Setup] -> "Interval"; 
#define E1733A_CI_MEASETUP_INTERVAL2_ITEMTEXT 53        // [Measurement Setup] -> "Interval"; 
#define E1733A_CI_MEASETUP_MEAAXISSEL_CHOOSING 27       // [Measurement Setup] -> "Current Axis"; 0: l, 1: 2, 2: 3, ......
#define E1733A_CI_MEASETUP_MODE_CHOOSING 24             // [Measurement Setup] -> "Travel Mode"; 0: Bidirectional, 1: Unidirectional, 2: Pilgrim, 
#define E1733A_CI_MEASETUP_OCFACTOR_ITEMTEXT 49         // [Measurement Setup] -> "Calibration Factor"; 
#define E1733A_CI_MEASETUP_PARATYPE_CHOOSING 52         // [Measurement Setup] -> "Parallelism"; 0: Spindle, 1: Coplanar, 
#define E1733A_CI_MEASETUP_POINTS_ITEMTEXT 18           // [Measurement Setup] -> "No. of Points"; 
#define E1733A_CI_MEASETUP_POINTS2_ITEMTEXT 55          // [Measurement Setup] -> "No. of Points" (Axis 2); 
#define E1733A_CI_MEASETUP_POSITIONS_ITEMTEXT 135       // [Measurement Setup] -> "Target Position"; 
#define E1733A_CI_MEASETUP_POSITIONS2_ITEMTEXT 136      // [Measurement Setup] -> "Target Position" (Axis 2); 
#define E1733A_CI_MEASETUP_POSUNIT_CHOOSING 40          // [Measurement Setup] -> "Position Units"; 0: mm, 1: inches, 2: arcdeg, 
#define E1733A_CI_MEASETUP_PRESET_ITEMTEXT 44           // [Measurement Setup] -> "Preset"; 
#define E1733A_CI_MEASETUP_RANGETYPE_CHOOSING 50        // [Measurement Setup] -> "Optics"; 0: Short Range, 1: Long Range, 
#define E1733A_CI_MEASETUP_RESULTRES_CHOOSING 38        // [Measurement Setup] -> "Display Resolution"; 0: 1, 1: 0.1, 2: 0.01, 3: 0.001, 4: 0.0001, 5: 0.00001, 6: 0.000001, 7: 0.0000001, 8: 0.00000001, 
#define E1733A_CI_MEASETUP_ROTAQBRES_ITEMTEXT 51        // [Measurement Setup] -> "Rotary Resolution"; 
#define E1733A_CI_MEASETUP_SQUAREERR_ITEMTEXT 45        // [Measurement Setup] -> "Optical Square"; 
#define E1733A_CI_MEASETUP_STARTPOS_ITEMTEXT 20         // [Measurement Setup] -> "Start Position"; 
#define E1733A_CI_MEASETUP_STARTPOS2_ITEMTEXT 57        // [Measurement Setup] -> "Start Position" (Axis 2); 
#define E1733A_CI_MEASETUP_TRIGDWELL_ITEMTEXT 32        // [Measurement Setup] -> "Trigger Dwell"; 
#define E1733A_CI_MEASETUP_TRIGTYPE_CHOOSING 34         // [Measurement Setup] -> "Trigger Type"; 0: Manual, 1: Encoder, 2: Auto
#define E1733A_CI_MEASETUP_TRIGWND_ITEMTEXT 36          // [Measurement Setup] -> "Target Window"; 
#define E1733A_CI_MEASETUP_UNITSYSSEL_CHOOSING 39       // [Measurement Setup] -> "Measurement Units"; 0: Metric, 1: English, 2: Metric , 3: English , 4: Metric  , 5: English  , 6: Angle & Metric, 7: Angle & English, 
#define E1733A_CI_MEASETUP_USERDEF_CHOOSING 21          // [Measurement Setup] -> "User Defined"; 0: No, 1: Yes, 
#define E1733A_CI_MEASETUP_USERDEF2_CHOOSING 54         // [Measurement Setup] -> "User Defined" (Axis 2); 0: No, 1: Yes, 
#define E1733A_CI_MEASETUP_WAYDIR_CHOOSING 23           // [Measurement Setup] -> "Direction"; 0: A->B, 1: B->A, 
#define E1733A_CI_MEASETUP_WAYSTANUM_ITEMTEXT 16        // [Measurement Setup] -> "# of Stations"; 
/*		SYSTEM	*/
#define E1733A_CI_SYSSETUP_BEEPREC_CHOOSING 4           // [System] -> "Beep on Record"; 0: No, 1: Yes, 
#define E1733A_CI_SYSSETUP_DEMOMODE_CHOOSING 3          // [System] -> "Demo Mode"; 0: No, 1: Yes, 
#define E1733A_CI_SYSSETUP_ROTARYDEV_CHOOSING 7         // [System] -> "Rotary Table"; 0: 55290A, 1: 55290B,
#define E1733A_CI_SYSSETUP_SYNCHOP_CHOOSING 5           // [System] -> "Synchronized Operation"; 0: No, 1: Yes,
#define E1733A_CI_SYSSETUP_WAVELENGTH_ITEMTEXT 6        // [System] -> "Laser Wavelength";
#define E1733A_CI_SYSSETUP_E1735ASN_ITEMTEXT 144        // [System] -> "E1735A: Serial No."; S/N string
#define E1733A_CI_SYSSETUP_E1735ASN_CHOOSING 153        // [System] -> "E1735A: Serial No."; 0: 1st device, 1: 2nd device, et. al.
#define E1733A_CI_SYSSETUP_E1736ASN_ITEMTEXT 145        // [System] -> "E1736A: Serial No."; S/N string
#define E1733A_CI_SYSSETUP_E1736ASN_CHOOSING 154        // [System] -> "E1736A: Serial No."; 0: 1st device, 1: 2nd device, et. al.
#define E1733A_CI_SYSSETUP_USERCALI_ITEMTEXT 149		// [System] -> "User Calibration"; for 55290B
#define E1733A_CI_SYSSETUP_CALIPERIOD_ITEMTEXT 159		// [System] -> [System] -> "Calibration Period"; in month
/*		TIME BASE	*/
#define E1733A_CI_TIMSETUP_POINTNUM_ITEMTEXT 65         // [Time Base] -> "No. of Points";
#define E1733A_CI_TIMSETUP_STARTTYPE_CHOOSING 63        // [Time Base] -> "Start Timer"; 0: Manual, 1: Position, 
#define E1733A_CI_TIMSETUP_STOPTYPE_CHOOSING 67         // [Time Base] -> "Stop Timer"; 0: Manual, 1: Position, 2: Total Time, 3: Total Points, 
#define E1733A_CI_TIMSETUP_TBINTERVAL_ITEMTEXT 61       // [Time Base] -> "Interval" (value);
#define E1733A_CI_TIMSETUP_TBINTERVAL_ITEMUNIT 146		// [Time Base] -> "Interval" (unit); "ms" or "sec", for all kinds of time-based
#define E1733A_CI_TIMSETUP_TBSTARTPOS_ITEMTEXT 62       // [Time Base] -> "Position" (Start);
#define E1733A_CI_TIMSETUP_TBSTOPPOS_ITEMTEXT 64        // [Time Base] -> "Position" (Stop);
#define E1733A_CI_TIMSETUP_TOTALTIME_ITEMTEXT 66        // [Time Base] -> "Total Time";
/*		E1733A MAIN	*/
#define E1733A_CI_TOPSETUP_DATAPATH_ITEMTEXT 2          // [E1733A] -> "Default Path";
#define E1733A_CI_TOPSETUP_LANGUAGE_CHOOSING 1          // [E1733A] -> "Language"; 0: English, 1: French, 3: German, 4: Spanish, 5: SimpChn, 6: TradChn, 7: Korean, 8: Japanese,
#define E1733A_CI_TOPSETUP_OPENSTYLE_CHOOSING 0         // [E1733A] -> "Setup"; 1: Default, 2: Saved, 4: Information,
#define E1733A_CI_TOPSETUP_SHOWHINT_CHOOSING 151        // [E1733A] -> "Show Hint"; 0: No, 1: Yes,
/*		Dual Axis	*/
#define E1733A_CI_XDASETUP_XDACARD1_ITEMTEXT 140		// [Dual Axes] -> "E1735A #1 Serial No."; S/N string
#define E1733A_CI_XDASETUP_XDACARD1_CHOOSING 155		// [Dual Axes] -> "E1735A #1 Serial No."; 0: (None), 1: 1st device, 2: 2nd device, et. al.
#define E1733A_CI_XDASETUP_XDAHUB1_ITEMTEXT 141			// [Dual Axes] -> "E1736A #1 Serial No."; S/N string
#define E1733A_CI_XDASETUP_XDAHUB1_CHOOSING 156			// [Dual Axes] -> "E1736A #1 Serial No."; 0: (None), 1: 1st device, 2: 2nd device, et. al.
#define E1733A_CI_XDASETUP_XDACARD2_ITEMTEXT 142		// [Dual Axes] -> "E1735A #2 Serial No."; S/N string
#define E1733A_CI_XDASETUP_XDACARD2_CHOOSING 157		// [Dual Axes] -> "E1735A #2 Serial No."; 0: (None), 1: 1st device, 2: 2nd device, et. al.
#define E1733A_CI_XDASETUP_XDAHUB2_ITEMTEXT 143			// [Dual Axes] -> "E1736A #2 Serial No."; S/N string
#define E1733A_CI_XDASETUP_XDAHUB2_CHOOSING 158			// [Dual Axes] -> "E1736A #2 Serial No."; 0: (None), 1: 1st device, 2: 2nd device, et. al.

// read data analysis results
// assign axis number to WParam.Num, 0 for all axes, 1 for axis 1, et. al.
// the value is returned by the message result, as a 4-byte integer, transfer it to float using TIntFloat
#define E1733A_CC_ANALYSIS 66       
#define E1733A_CI_BIMAXREV 0		// B, max reversl error
#define E1733A_CI_BIMEANREV 1		// ~B, mean reversal error
#define E1733A_CI_BIMEANDEV 2		// M, mean bi-directional positin deviation
#define E1733A_CI_REVSYSPOSDEV 3	// E-, Mean positional deviation, backward
#define E1733A_CI_FWDSYSPOSDEV 4	// E+, Mean positional deviation, forward
#define E1733A_CI_BISYSPOSDEV 5		// E, Mean positional deviation, bi-directional
#define E1733A_CI_REVREPEATPOS 6	// R-, Repeatabolity, backward
#define E1733A_CI_FWDREPEATPOS 7	// R+, Repeatabolity, forward
#define E1733A_CI_BIREPEATPOS 8		// R, Repeatabolity, bi-directional
#define E1733A_CI_REVACCURACY 9		// A-, Accuracy, backward
#define E1733A_CI_FWDACCURACY 10	// A+, Accuracy, forward
#define E1733A_CI_BIACCURACY 11		// A, Accuracy, bi-directional
#define E1733A_CI_REVRAWREP 12		// R-', Raw Repeatabolity, backward
#define E1733A_CI_FWDRAWREP 13		// R+', Raw Repeatabolity, forward
#define E1733A_CI_BIRAWREP 14		// R', Raw Repeatabolity, bi-directional
#define E1733A_CI_REVRAWACC 15		// A-', Raw Accuracy, backward
#define E1733A_CI_FWDRAWACC 16		// A+', Raw Accuracy, forward
#define E1733A_CI_BIRAWACC 17		// A', Raw Accuracy, bi-directional
#define E1733A_CI_SIXSIGMA 18		// 6*sigma, six times of standard deviation
#define E1733A_CI_SLOPELS 19		// slope, least square method
#define E1733A_CI_SLOPEEP 20		// slope, end point method
#define E1733A_CI_VDI_P 21			// VDI standard, positional uncertainty
#define E1733A_CI_VDI_PSMAX 22		// VDI standard, maximum positional scatter
#define E1733A_CI_VDI_PSMEAN 23		// VDI standard, mean positional scatter
#define E1733A_CI_VDI_PSU 24		// VDI standard, positional scatter and uncertainty 
#define E1733A_CI_VDI_PA 25			// VDI standard, position deviation
#define E1733A_CI_VDI_UMAX 26		// VDI standard, reversal error
#define E1733A_CI_VDI_UMEAN 27		// VDI standard, mean reversal error
#define E1733A_CI_MAX_ELEVATION 30	// Num=0 for all axes, 1 for axis 1, ...
#define E1733A_CI_PLUSMINUS 35		// Plus/Minus value
#define E1733A_CI_CLOSURE_DH 31		// Closure between DH, flatness only
#define E1733A_CI_CLOSURE_BF 32		// Closure between BF, flatness only
#define E1733A_CI_PAR_RESULT 33		// parallelism result
#define E1733A_CI_SQU_RESULT 34		// squareness result
#define E1733A_CI_POS_MAX 40		// maximum position, time base only
#define E1733A_CI_POS_MIN 41		// minimum position, time base only
#define E1733A_CI_POS_MEAN 42		// mean position, time base only
#define E1733A_CI_POS_NSIGMA 43		// N*Sigma position, time base only
#define E1733A_CI_VEL_MAX 44		// maximum velocity, time base only
#define E1733A_CI_VEL_MIN 45		// minimum velocity, time base only
#define E1733A_CI_VEL_MEAN 46		// mean velocity, time base only
#define E1733A_CI_VEL_NSIGMA 47		// N*Sigma velocity, time base only
#define E1733A_CI_ACC_MAX 48		// maximum acceleration, time base only
#define E1733A_CI_ACC_MIN 49		// minimum acceleration, time base only
#define E1733A_CI_ACC_MEAN 50		// mean acceleration, time base only
#define E1733A_CI_ACC_NSIGMA 51		// N*Sigma acceleration, time base only
