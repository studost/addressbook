#!/usr/bin/perl
#=======================================================================================
# Copyright
# SECTOR NORD AG
# 2014-05-30-17-14-12
# UST
#=======================================================================================
# Introduction
#=======================================================================================
# This PlugIn provides
#
# Config Firefox
# Open page about:config
# Add value network.protocol-handler.expose.tviewer boolean false
# Open URL tviewer://123456 in FF an configure the program /home/studo/projects/misc/utils/tviewer (shell)
# 2015-04-06, Redirect to serverlist.cgi?s_name=param('name') after action save (sub back_to_main)
# 
#=======================================================================================
# Pragmas
#=======================================================================================
use strict;
use warnings;
use Data::Dumper;
$Data::Dumper::Sortkeys = 1;

# Get the base name of this script for use in the examples
use File::Basename;

use CGI qw(:standard);
use CGI::Carp qw(fatalsToBrowser);

# http://de.selfhtml.org/perl/module/cgi.htm#umgebungsdaten
my $cgi = new CGI;
my $script_name = $cgi->script_name();

use DBI;

#=======================================================================================
# Variables
#=======================================================================================
# formular search
my $company     = param("s_company")    ||  'NOTSETYET';
my $name        = param("s_name")       ||  'NOTSETYET';
my $ip          = param("s_ip")         ||  'NOTSETYET';
my $user        = param("s_user")       ||  'NOTSETYET';
my $comment     = param("s_comment")    ||  'NOTSETYET';
my $misc        = param("s_misc")       ||  'NOTSETYET';

my $search = {
    'company'     => $company,
    'name'        => $name,
    'ip'          => $ip,
    'user'        => $user,
    'comment'     => $comment,
    'misc'        => $misc,
};

#=======================================================================================
# 
#=======================================================================================
my %actions = (
    'default'           => \&start_page,
    'search'            => \&search_server,
    'edit'              => \&edit_server,
    'copy'              => \&copy_server,
    'delete'            => \&delete_server,
    'save'              => \&save_server,
);

my $current_page = param('action') || 'default';
#die "No page for $current_page" unless $actions{$current_page};
my $action = param('action') || 'default';

#=======================================================================================
# Main
#=======================================================================================
#print header,
#start_html('A Simple Example'),
#h1('A Simple Example'),
#####
# TODO: switch
if ($action eq 'default') {
    start_page();
}
elsif ($action eq 'save') {
    save_server();
}
elsif ($action eq 'delete') {
    delete_server();
}
elsif ($action eq 'edit') {
    edit_server();
}
else {
    die "No page for $action";
}






#=======================================================================================
# subprocedures
#=======================================================================================
#=============================
# sub start_page
#=============================
sub start_page {
    page_header();
    warn("company is: $search->{'company'}");
    warn("ip is: $search->{'ip'}");
    
    my $dbh = db_connect();
    my @server = get_server($dbh, $search);
    foreach my $server (@server) {
        format_table_row($server);
    }
    print '</form>';
    
    page_footer();
}

#=============================
# sub save_server
#=============================
sub save_server {
    page_header();
    
    my $dbh = db_connect();
#| name    | varchar(25) | NO   |     | NULL    |                |
#| company | varchar(25) | NO   |     | None    |                |
#| ip      | varchar(25) | NO   |     | None    |                |
#| user    | varchar(25) | YES  |     | None    |                |
#| comment | varchar(50) | YES  |     | None    |                |
#| misc    | varchar(50) | YES  |     | None
    my $id          = param('id');
    my $company     = $dbh->quote(param('company'));
    my $name        = $dbh->quote(param('name'));
    my $ip          = $dbh->quote(param('ip'));
    my $user        = $dbh->quote(param('user')     || 'None');
    my $comment     = $dbh->quote(param('comment')  || 'None');
    my $misc        = $dbh->quote(param('misc')     || 'None');

    unless ( $company && $name && $ip) {
        die( 'Please supply company, name, and ip address for the server');
    }
    my $sql = '';
    if ($id) {
        $sql = sprintf('UPDATE serverlist SET company = %s, name = %s, ip = %s, user = %s, comment = %s, misc = %s 
        WHERE id=%i', $company, $name, $ip, $user, $comment, $misc, int($id));
    }
    else {
        $sql = sprintf('INSERT INTO serverlist (company, name, ip, user, comment, misc) VALUES( %s, %s, %s, %s, %s, %s )',
        $company, $name, $ip, $user, $comment, $misc);
    }
    print pre($sql);
    eval {
        $dbh->do($sql) or warn $dbh->errstr;
        #print pre("ERROR is: ".$dbh->{Statement});
        $dbh->commit();
        # Disconnect from the database.
        $dbh->disconnect();
    };
    if ($@) {
        print pre("ERROR is: ".$DBI::lasth->errstr);
        warn("ERROR is: ".$DBI::lasth->errstr);
    }
    back_to_main( 1, 'New server '.$name.' added to serverlist', param('name') );
}

#=============================
# sub delete_server
#=============================
sub delete_server {
    page_header();
    
    my $dbh = db_connect();
    
    my $id       = int(param('id'));

    unless ( $id) {
        die( 'Please supply an id to delete a server');
    }
    my $sql = sprintf('DELETE FROM serverlist WHERE id=%i', $id);
    print pre($sql);
    eval {
        $dbh->do($sql) or warn $dbh->errstr;
        #print pre("ERROR is: ".$dbh->{Statement});
        $dbh->commit();
        # Disconnect from the database.
        $dbh->disconnect();
    };
    if ($@) {
        print pre("ERROR is: ".$DBI::lasth->errstr);
        die("ERROR is: ".$DBI::lasth->errstr);
    }
    back_to_main( 1, 'Deleted server with id '.$id);
}

#=============================
# sub edit_server
#=============================
sub edit_server {
    page_header();
    
    my $id       = int(param('id'));
    unless ( $id) {
        die( 'Please supply an id to edit a server');
    }
    
    my $dbh = db_connect();
    
    my $sql = sprintf('SELECT * FROM serverlist WHERE id=%i', $id);
    my $sth = $dbh->prepare($sql);
    $sth->execute();
    
    my $numRows = $sth->rows;
    print pre("Could not find a server within database.") unless $numRows;
    print pre( "Number of rows is: " . $numRows);
    my $row = $sth->fetchrow_hashref;
    my $output = "id: $row->{'id'}\tcustomer: $row->{'customer'}\tname: $row->{'name'}";
    warn( $output );
    $dbh->disconnect();
    
print << "_END_OF_TEXT_";
<form action="$script_name" method="post">
    <input type="hidden" name="id" value="$id"/>
        <tr>
            <td><input type="text" name="company" value="$row->{'company'}" /></td>
            <td></td>
            <td><input type="text" name="ip" value="$row->{'ip'}" /></td>
            <td><input type="text" name="name" value="$row->{'name'}" /></td>
            <td><input type="text" name="user" value="$row->{'user'}" /></td>
            <td><input type="text" name="comment" value="$row->{'comment'}" /></td>
            <td><input type="text" name="misc" value="$row->{'misc'}" /></td>
            <td></td>
            <td>
                <input name="action" type="submit" value="save" name="End edit">
                <!-- <a class="btn btn-danger" href="save.cgi"><i class="glyphicon glyphicon-remove"></i></a> -->
            </td>
        </tr>
        </tbody>
    </table>
</form>
</div>
</body>
</html>
_END_OF_TEXT_
    
    #<input name="action" type="submit" value="save">
    #<!-- <a class="btn btn-danger" href="save.cgi"><i class="glyphicon glyphicon-remove"></i></a> -->
    #back_to_main(1, 'Edited server with id '.$id);
}

#=============================
# sub page_header
#=============================
sub page_header {
print "Content-type: text/html\n\n";

print << "_END_OF_TEXT_";
<!DOCTYPE html>
<html>
<head lang="en">
    <meta charset="UTF-8">
    <title></title>
    <!-- Latest compiled and minified CSS -->
    <link rel="stylesheet" href="//netdna.bootstrapcdn.com/bootstrap/3.1.1/css/bootstrap.min.css">

    <!-- Optional theme -->
    <link rel="stylesheet" href="//netdna.bootstrapcdn.com/bootstrap/3.1.1/css/bootstrap-theme.min.css">

    <!-- Latest compiled and minified JavaScript -->
    <script src="//netdna.bootstrapcdn.com/bootstrap/3.1.1/js/bootstrap.min.js"></script>
</head>
<body>
<div class="container-fluid">

        <!--
    <div class="page-header">
        <h1>The Foobar serverlist</h1>
        <p class="lead">Select an entry from my amazing private serverlist!</p>
    </div>
        -->
    <table class="table table-bordered">
        <thead>
        <tr>
                <td>Company</td>
                <td></td>
                <td>IP</td>
                <td>Name</td>
                <td>User</td>
                <td>Comment</td>
                <td>Misc</td>
                <td></td>
                <td></td>
        </tr>
        </thead>
    <form action="serverlist.cgi" method="get">
            <tr>
                <td><input type="text" name="s_company"></td>
                <td></td>
                <td><input type="text" name="s_ip"></td>
                <td><input type="text" name="s_name"></td>
                <td><input type="text" name="s_user"></td>
                <td><input type="text" name="s_comment"></td>
                <td><input type="text" name="s_misc"></td>
                <td></td>
                <td>
                    <input type="submit" value="search">
                </td>
            </tr>
    </form>
_END_OF_TEXT_
}

#=============================
# sub page_footer
#=============================
sub page_footer {
print << "_END_OF_TEXT_";
    <form action="serverlist.cgi" method="post">
            <tr>
                <td><input type="text" name="company"/></td>
                <td></td>
                <td><input type="text" name="ip"/></td>
                <td><input type="text" name="name"/></td>
                <td><input type="text" name="user"/></td>
                <td><input type="text" name="comment"/></td>
                <td><input type="text" name="misc"/></td>
                <td></td>
                <td>
                    <input name="action" type="submit" value="save">
                    <!-- <a class="btn btn-danger" href="save.cgi"><i class="glyphicon glyphicon-remove"></i></a> -->
                </td>
            </tr>
        </tbody>
        </table>
    </form>
    </div>
    </body>
    </html>
_END_OF_TEXT_

}

#=============================
# sub format_table_row
#=============================
sub format_table_row {
my $row = shift;
# wilhelm.tel:start.md
my $company_url = 'http://localhost/dokuwiki/doku.php?id=cnotes:customer:'.lc($row->{'company'}).':start.md';
my $ssh_str = 'ssh://'.$row->{'user'}.'@'.$row->{'ip'};
#my $ssh_str = $row->{'user'} eq 'None' ? 'ssh://'.$row->{'ip'} : 'ssh://'.$row->{'user'}.'@'.$row->{'ip'};
#my $email_str = nice_string($row->{'email'}, 18);
#my $comment_str = ($row->{'comment'} eq 'NOTSETYET' ? 'None' : $row->{'comment'});

print << "_END_OF_TEXT_";
<tr>
    <td><a href="$company_url" target="_blank" >$row->{'company'}</a> </td
    <td></td>
    <td><a class="btn btn-info" href="phonebook.cgi?s_company=$row->{'company'}" target="_blank" ><i class="glyphicon glyphicon-edit"></i></a></td>
    <td> <a href="http://$row->{'ip'}" target="_blank" >$row->{'ip'}</a> </td>
    <td>
        $row->{'name'}
    </td>
    <td>
        $row->{'user'}
    </td>
    <td>
        $row->{'comment'}
    </td>
    <td>
        $row->{'misc'}
    </td>
    <td>
        <a class="btn btn-info" href="$ssh_str"><i class="glyphicon glyphicon-copyright-mark"></i></a>
    </td>
    <td>
        <a class="btn btn-success" href="$script_name?action=edit&id=$row->{'id'}"><i class="glyphicon glyphicon-edit"></i></a>
        <!-- <a class="btn btn-info" href="$script_name?action=copy&id=$row->{'id'}"><i class="glyphicon glyphicon-copyright-mark"></i></a> -->
        <a class="btn btn-danger" href="$script_name?action=delete&id=$row->{'id'}"><i class="glyphicon glyphicon-trash"></i></a>
    </td>
</tr>
_END_OF_TEXT_

}

#=============================
# sub db_connect
#=============================
sub db_connect {
    my $dbName = 'phonebook';
    my $dbHost = 'localhost';
    my $dbUser = 'root';
    my $dbPass = 'sector';

    my $dbh = DBI->connect(
        "DBI:mysql:$dbName:$dbHost",
        "$dbUser",
        "$dbPass",
        {   RaiseError => 1,
            PrintError => 1,
            AutoCommit => 0
        }
    );
    return $dbh;
}

#=============================
# sub get_servers
#=============================
sub get_server {
    my $dbh = shift;
    my $sth;
    my $search = shift;
    my @server;
    my @clauses;
    my @bind;
    # Now retrieve data from the table.
    my $sql = '';
    if ($search->{'company'} ne 'NOTSETYET') {
        push @clauses, "company LIKE ?";
        push @bind, '%'.$search->{'company'}.'%';
    }
    if ($search->{'name'} ne 'NOTSETYET') {
        push @clauses, 'name LIKE ?';
        push @bind, '%'.$search->{'name'}.'%';
    }
    if ($search->{'ip'} ne 'NOTSETYET') {
        push @clauses, 'ip LIKE ?';
        push @bind, '%'.$search->{'ip'}.'%';
    }
    if ($search->{'user'} ne 'NOTSETYET') {
        push @clauses, 'user LIKE ?';
        push @bind, '%'.$search->{'user'}.'%';
    }
    if ($search->{'comment'} ne 'NOTSETYET') {
        push @clauses, 'comment LIKE ?';
        push @bind, '%'.$search->{'comment'}.'%';
    }
    if ($search->{'misc'} ne 'NOTSETYET') {
        push @clauses, 'misc LIKE ?';
        push @bind, '%'.$search->{'misc'}.'%';
    }
    if (@clauses) {
        my $clause = join(' AND ', @clauses);
        $sql = "SELECT * FROM serverlist WHERE $clause";
        print pre( "Query is: " . $sql);
        $sth = $dbh->prepare($sql);
        $sth->execute(@bind);
        #$sth->execute( "Avebury", "%largest stone circle%" );
    }
    else {
        $sql = 'SELECT * FROM serverlist ORDER BY company, ip';
        $sth = $dbh->prepare($sql);
        $sth->execute();
    }
    my $numRows = $sth->rows;
    print pre("Could not find a server within database.") unless $numRows;
    print pre( "Number of rows is: " . $numRows);
    while (my $row = $sth->fetchrow_hashref) {
        warn( Dumper($row) );
        my %server = ();
        my $output = "id: $row->{'id'}\tcompany: $row->{'company'}\tname: $row->{'name'}";
        warn($output);
        $server{'id'}               = $row->{'id'};
        $server{'company'}          = $row->{'company'};
        $server{'name'}             = $row->{'name'};
        $server{'ip'}               = $row->{'ip'};
        $server{'user'}             = $row->{'user'};
        $server{'comment'}          = $row->{'comment'};
        $server{'misc'}             = $row->{'misc'};
        push(@server, \%server);
    } # END while
    $sth->finish();
    # Disconnect from the database.
    $dbh->disconnect();
    return @server;
}

#=============================
# sub back_to_main
#=============================
sub back_to_main {
    my $timeout = shift || 5;
    my $title = shift || 'New server added to database';
    my $name = shift || '';
    my $url = ( $name ? $script_name.'?s_name='.$name : $script_name );
    warn("url is: $url");

#TODO
print << "_END_OF_TEXT_";
<html>
    <head>
      <title>$title</title>
    <meta http-equiv="refresh" content="$timeout; URL=$url">
    <!-- ... andere Angaben im Dateikopf ... -->
    </head>
    <body>
        <h1>$title</h1>
        <hr />
        <!-- <h2>URL is $url</h2> -->
        <a href="$script_name">Back to the main page</a>
    </body>
</html>
_END_OF_TEXT_

}

#=============================
# sub nice_string
#=============================
sub nice_string {
    my ($str, $len) = @_;
    if ($str eq '') {
        return 'None';
    }
    else {
        if (length($str) < int($len)) {
            return $str;
        }
        else {
            return substr($str, 0, int($len)).'...';
        }
    }
}
