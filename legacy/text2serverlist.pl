#!/usr/bin/perl
# nagios: -epn
#=======================================================================================
# Copyright
# UST
#=======================================================================================
# text2serverlist.pl
# Import tab separated list of servers into MySQL db phonebook table serverlist
#=======================================================================================
# This PlugIn provides ...
#
# TODO:
#
# ERRORS:
#
# CHANGELOG:
#
#=======================================================================================
# Pragmas
#=======================================================================================
use strict;
use warnings;

use FindBin;
use lib $FindBin::Bin . '/perl/lib';

# Load required Perl modules
use Nagios::Plugin;
use SVUtils;
use Data::Dumper;

# DBD database driver for MySQL
use DBI;

# Get the base name of this script for use in the examples
use File::Basename;
my $PROGNAME = basename($0);

use constant {
    STD => 0,
    INF => 1,
    DBG => 2,
    SPM => 3,
};

#=======================================================================================
# Variables
#=======================================================================================
my $RELEASE = '1.0.0';
my $BUILD   = '2018-05-31';

my $VERSION = " Plugin\nVersion: $RELEASE\nBuild: $BUILD\n(C) 2018 ";
my $LICENSE = "";    # Lizenz wird in der Version mit ausgegeben (sonst taucht sie nicht bei --version auf!)
my $URL = "http://www.sectornord.de";

#=======================================================================================
# Hack for avoiding a label in front of "OK" or "CRITICAL", in order to conform
# to the usual Nagios conventions and to use redundancy in the UI display.
#=======================================================================================
BEGIN {
    no warnings 'redefine';
    *Nagios::Plugin::Functions::get_shortname = sub {
        return undef;
    };
}

#=======================================================================================
# Command line options
# Define and get the command line options.
# See the command line option guidelines at
# http://nagiosplug.sourceforge.net/developer-guidelines.html#PLUGOPTIONS
#=======================================================================================
# Instantiate Nagios::Plugin object (the 'usage' parameter is mandatory)
my $svplugin = Nagios::Plugin->new(
    shortname => "",
    version   => $VERSION,
    license   => $LICENSE,
    url       => $URL,
    timeout   => 15,
    usage     => '',
    blurb     => '',
    extra     => '',
);

#=======================================================================================
# Define and document the valid command line options
# usage, help, version, timeout and verbose are defined by default.
#=======================================================================================
$svplugin->add_arg(
    spec => 'mode|M=s',
    help => qq{-M, --mode=Plug-in mode
	Available modes are:
	- import_server
	},
    required => 1,
    default  => 'import_server',
);
$svplugin->add_arg(
    spec => 'file|F=s',
    help => qq{-F, --file= < Name of the import file >
	},
    required => 1,
    default  => '/var/lib/dokuwiki/data/pages/cnotes/serverliste.md.txt',
);
$svplugin->add_arg(
    spec => 'host|H=s',
    help => qq{-H, --host=database host
	Address of the database server.},
    required => 1,
    default  => 'localhost',
);

#=======================================================================================
# Parse arguments and process standard ones (e.g. usage, help, version)
#=======================================================================================
$svplugin->getopts;

#=======================================================================================
# Perform sanity checking on command line options
#=======================================================================================
unless ( defined $svplugin->opts->file ) {
    $svplugin->nagios_die("You didn't supply a import file");
}
if ( $svplugin->opts->host eq '' ) {
    $svplugin->nagios_die("Host has to be defined.");
}
#
#if ( $svplugin->opts->mode eq '' ) {
#    $svplugin->nagios_die("Mode for plug-in has to be defined.");
#}
#
#if ( $svplugin->opts->mode eq 'newTab' && $svplugin->opts->tab eq 'EMPTY' ) {
#    $svplugin->nagios_die("No name for new tab given.");
#}
#
#if ( $svplugin->opts->mode eq 'copyTab' && $svplugin->opts->tab eq 'EMPTY' ) {
#    $svplugin->nagios_die("No name for new tab given.");
#}

#=======================================================================================
# Define Debugging with Perl module SVUtils.pm
#=======================================================================================
$SVUtils::VERBOSE = $svplugin->opts->verbose;

#=======================================================================================
# Activate timeout.
# THIS is where you'd do your actual checking to get a real value for $result
# Don't forget to timeout after $p->opts->timeout seconds, if applicable.
#=======================================================================================
#--------------------------------------------------
# my $timeout = $svplugin->opts->timeout;
# &logger(3, "Timeout is: $timeout");
# $SIG{ALRM} = sub {
# 	$svplugin->nagios_die("Plugin $PROGNAME reached timeout of $timeout seconds");
# };
#--------------------------------------------------

# alarm $svplugin->opts->timeout;
# alarm($timeout);

#=======================================================================================
# MAIN
# THIS is where you'd do your actual checking to get a real value for $checkresult
#=======================================================================================
# my $time = &calculateTime($svplugin->opts->time) if $svplugin->opts->time;
my $dbh;
my $result;
my $import_file = $svplugin->opts->file;

if ( $svplugin->opts->mode eq 'import_server' ) {
    $dbh = db_connect();
    $svplugin->nagios_die("Could not connect to database.") unless $dbh;
    my $server_list = get_server($import_file);
    logger( INF, "server are: ".join("\n", @$server_list));
    $result = import_server($server_list);
    logger( STD, "result is: ".$result);
}
elsif ( $svplugin->opts->mode eq 'copyTab' ) {
    $dbh = db_connect();
    $svplugin->nagios_die("Could not connect to database.") unless $dbh;
    my ( $oldTab, $newTab ) = split( ',', $svplugin->opts->tab );
    $result = &copyTab( $oldTab, $newTab );
}
elsif ( $svplugin->opts->mode eq 'updateChecks' ) {
    $dbh = db_connect();
    $svplugin->nagios_die("Could not connect to database.") unless $dbh;
    &logger( 1, "Updating check intervals!" );
    $result = &updateChecks();
}
else {
    $svplugin->nagios_die("Unknown mode $svplugin->opts->mode!");

}

# Print message and exit Plugin with correct exit code
#--------------------------------------------------
# $svplugin->nagios_exit(
# 		return_code => $returnCode,
# 		message => $output,
# );
#--------------------------------------------------

# ALARM STOP
# alarm(0);

# EXIT - we never should come here
$svplugin->nagios_die("Plugin exits here - something went terribly wrong");

#=======================================================================================
# subprocedures
#=======================================================================================
#=============================
# sub dbConnect
#=============================
sub db_connect {
    my $dbName = 'phonebook';
    my $dbHost = $svplugin->opts->host;
    my $dbUser = 'root';
    my $dbPass = 'sector';

    my $dbh = DBI->connect(
        "DBI:mysql:$dbName:$dbHost",
        "$dbUser",
        "$dbPass",
        {   RaiseError => 1,
            AutoCommit => 0
        }
    );
    return $dbh;
}

#=============================
# sub import_server
#=============================
sub import_server {
    my $server_list = shift;
    foreach my $server ( @$server_list ) {
        logger( STD, "Server is: ".$server->{'name'});
        my $sql = sprintf('INSERT INTO serverlist (company, name, ip, user, comment, misc) VALUES( "%s", "%s", "%s", "%s", "%s", "%s" )',
        'SectorNord', $server->{'name'}, $server->{'ip'}, 'None', $server->{'comment'}, 'None');
        logger( INF, "SQL is: $sql");
        eval {
            $dbh->do($sql) or warn $dbh->errstr;
            #print pre("ERROR is: ".$dbh->{Statement});
        };
        if ($@) {
            logger( STD, "ERROR is: ".$DBI::lasth->errstr);
        }
    }
    $dbh->commit();
    # Disconnect from the database.
    $dbh->disconnect();
    #logger( DBG, "db_insert_server is: $db_insert_server" );
    #my $rowsAffected = $dbh->do($db_insert_server);
    #logger( STD, "Inserted $rowsAffected new entries into serverlist" );
    #$dbh->commit;
    #$dbh->disconnect;
}

#=============================
# sub get_server
#=============================
sub get_server {
    my $import_file = shift;
    my @server;
    open( CONFIG, "<", $import_file )
        or die( "Could'nt open file $import_file for reading:", $! );

    while ( my $line = <CONFIG> ) {
        next if $line =~ /^\s*$/;
        next if $line =~ /^\s*[#;]/;
        #next if ( $line !~ /^\s*\S+\s*=.*$/ );
        chomp $line;
        my ( $ip, $name, $comment ) = split( '\t+', $line, 3 );
        my $server = {
            'ip'    => $ip,
            'name'  => $name,
            'comment'   => $comment,
        };
        push (@server, $server);
        #if ( $line =~ /^\s*(\w+)\s*=\s*(\w+)\s*$/) {
        #        my $key = $1;
        #        my $value = $2 ;
        #        # put them into hash
        #        $config->{$section}{$key} = $value;
        #    }
        # Remove whitespaces at the beginning and at the end
        #$key   = trim($key);
        #$value = trim($value);
        #die
        #    "Configuration option '$key' defined twice in line $lc of configuration file '$import_file'"
        #    if ( $config->{$section}{$key} );

        #$config->{$section}{$key} = $value;
    }    # END whilerver
    return \@server;
}

