#!/usr/bin/perl
#=======================================================================================
# Copyright
# SECTOR NORD AG
# 2014-04-30-11-05-51
# UST
#=======================================================================================
# Introduction
#=======================================================================================
# This PlugIn provides
#
# Config Firefox
# Open page about:config
# Add value network.protocol-handler.expose.tviewer boolean false
# Open URL tviewer://123456 in FF an configure the program /home/studo/projects/studo/misc/utils/tviewer (shell)
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
my $company     = param("s_company") ||  'NOTSETYET';
my $name        = param("s_name") ||  'NOTSETYET';
my $phone       = param("s_phone") ||  'NOTSETYET';
my $tviewer     = param("s_tviewer") ||  'NOTSETYET';
my $email       = param("s_email") ||  'NOTSETYET';
my $comment     = param("s_comment") ||  'NOTSETYET';

my $search = {
    'company'     => $company,
    'name'        => $name,
    'phone'       => $phone,
    'tviewer'     => $tviewer,
    'email'       => $email,
};

#=======================================================================================
# 
#=======================================================================================
my %actions = (
    'default'           => \&start_page,
    'search'            => \&search_contact,
    'edit'              => \&edit_contact,
    'copy'              => \&copy_contact,
    'delete'            => \&delete_contact,
    'save'              => \&save_contact,
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
    save_contact();
}
elsif ($action eq 'delete') {
    delete_contact();
}
elsif ($action eq 'edit') {
    edit_contact();
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
    
    my $dbh = db_connect();
    my @contacts = get_contacts($dbh, $search);
    print '<form action="edit.cgi" method="post">';
    #print '<form action="phonebook.cgi" method="post">';
    foreach my $contact (@contacts) {
        format_table_row($contact);
    }
    print '</form>';
    
    page_footer();
}

#=============================
# sub save_contact
#=============================
sub save_contact {
    page_header();
    
    my $dbh = db_connect();
    
    my $pb_id       = param('id');
    my $company     = $dbh->quote(param('company'));
    my $name        = $dbh->quote(param('name'));
    my $phone       = $dbh->quote(param('phone'));
    my $tviewer     = $dbh->quote(param('tviewer')  || 'NOTSETYET');
    my $email       = $dbh->quote(param('email')    || 'NOTSETYET');
    my $comment     = $dbh->quote(param('comment')  || 'NOTSETYET');

    unless ( $company && $name && $phone) {
        die( 'Please supply company, name, and phone');
    }
    my $sql = '';
    if ($pb_id) {
        $sql = sprintf('UPDATE phonebook SET company = %s, name = %s, phone = %s, tviewer = %s, email = %s, comment = %s 
        WHERE id=%i', $company, $name, $phone, $tviewer, $email, $comment, int($pb_id));
    }
    else {
        $sql = sprintf('INSERT INTO phonebook (company, name, phone, tviewer, email, comment) VALUES( %s, %s, %s, %s, %s, %s )',
        $company, $name, $phone, $tviewer, $email, $comment);
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
    back_to_main( 1, 'New contact added to phonebook', param('name') );
}

#=============================
# sub delete_contact
#=============================
sub delete_contact {
    page_header();
    
    my $dbh = db_connect();
    
    my $pb_id       = int(param('id'));

    unless ( $pb_id) {
        die( 'Please supply an id to delete a contact');
    }
    my $sql = sprintf('DELETE FROM phonebook WHERE id=%i', $pb_id);
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
    back_to_main( 1, 'Deleted contact with id '.$pb_id );
}

#=============================
# sub edit_contact
#=============================
sub edit_contact {
    page_header();
    
    my $pb_id       = int(param('id'));
    unless ( $pb_id) {
        die( 'Please supply an id to edit a contact');
    }
    
    my $dbh = db_connect();
    
    my $sql = sprintf('SELECT * FROM phonebook WHERE id=%i', $pb_id);
    my $sth = $dbh->prepare($sql);
    $sth->execute();
    
    my $numRows = $sth->rows;
    print pre("Could not find a contact within database.") unless $numRows;
    print pre( "Number of rows is: " . $numRows);
    my $row = $sth->fetchrow_hashref;
    my $output = "id: $row->{'id'}\tcustomer: $row->{'customer'}\tname: $row->{'name'}";
    warn( $output );
    $dbh->disconnect();
    
print << "_END_OF_TEXT_";
<form action="phonebook.cgi" method="post">
    <input type="hidden" name="id" value="$pb_id"/>
        <tr>
            <td><input type="text" name="company" value="$row->{'company'}" /></td>
            <td></td>
            <td><input type="text" name="name" value="$row->{'name'}" /></td>
            <td><input type="text" name="phone" value="$row->{'phone'}" /></td>
            <td><input type="text" name="tviewer" value="$row->{'tviewer'}" /></td>
            <td><input type="text" name="email" value="$row->{'email'}" /></td>
            <td><input type="text" name="comment" value="$row->{'comment'}" /></td>
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
    #back_to_main(1, 'Edited contact with id '.$pb_id);
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

<!--    <div class="page-header">
        <h1>The Foobar telephone book</h1>
        <p class="lead">Select an entry from my amazing private telephone book!</p>
    </div>
-->
    <table class="table table-bordered">
        <thead>
            <tr>
                <td>Company</td>
                <td></td>
                <td>Name</td>
                <td>Phone</td>
                <td>TViewer</td>
                <td>Email</td>
                <td>Comment</td>
                <td></td>
            </tr>
        </thead>
    <form action="phonebook.cgi" method="get">
            <tr>
                <td><input type="text" name="s_company"></td>
                <td></td>
                <td><input type="text" name="s_name"></td>
                <td><input type="text" name="s_phone"></td>
                <td><input type="text" name="s_tviewer"></td>
                <td><input type="text" name="s_email"></td>
                <td><input type="text" name="s_comment"></td>
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
    <form action="phonebook.cgi" method="post">
            <tr>
                <td><input type="text" name="company"/></td>
                <td></td>
                <td><input type="text" name="name"/></td>
                <td><input type="text" name="phone"/></td>
                <td><input type="text" name="tviewer"/></td>
                <td><input type="text" name="email"/></td>
                <td><input type="text" name="comment"/></td>
                <td>
                    <input name="action" type="submit" value="save">
                    <!-- <a class="btn btn-danger" href="save.cgi"><i class="glyphicon glyphicon-remove"></i></a> -->
                </td>
            </tr>
            </tbody>
        </table>
    </form>
    <a href='$script_name'>Back to the main page</a>
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
# 
my $company_url = 'http://localhost/dokuwiki/doku.php?id=cnotes:customer:'.lc($row->{'company'}).':start.md';
my $email_str = nice_string($row->{'email'}, 18);
my $tviewer_str = ($row->{'tviewer'} eq 'NOTSETYET' ? 'None' : $row->{'tviewer'});
my $comment_str = ($row->{'comment'} eq 'NOTSETYET' ? 'None' : $row->{'comment'});
print << "_END_OF_TEXT_";
<tr>
    <td>
        <a href="$company_url" target="_blank" >$row->{'company'}</a>
    </td>
    <td>
        <a class="btn btn-success" href="serverlist.cgi?s_company=$row->{'company'}" target="_blank" ><i class="glyphicon glyphicon-edit"></i></a>
    </td>
    <td>
        $row->{'name'}
    </td>
    <td>
        $row->{'phone'}
    </td>
    <td>
        <a href="tviewer://$row->{'tviewer'}">$tviewer_str</a>
    </td>
    <td>
        <a href="mailto:$row->{'email'}">$email_str</a>
    </td>
    <td>
        $comment_str
    </td>
    <td>
        <a class="btn btn-success" href="phonebook.cgi?action=edit&id=$row->{'id'}"><i class="glyphicon glyphicon-edit"></i></a>
        <!-- <a class="btn btn-info" href="phonebook.cgi?action=copy&id=$row->{'id'}"><i class="glyphicon glyphicon-copyright-mark"></i></a> -->
        <a class="btn btn-danger" href="phonebook.cgi?action=delete&id=$row->{'id'}"><i class="glyphicon glyphicon-trash"></i></a>
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
# sub get_contacts
#=============================
sub get_contacts {
#curs.execute('SELECT * FROM phonebook ORDER BY company, name')
#rows = curs.fetchall()
#for row in rows:
    #format(row)
    my $dbh = shift;
    my $sth;
    my $search = shift;
    my @contacts;
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
    if ($search->{'phone'} ne 'NOTSETYET') {
        push @clauses, 'phone LIKE ?';
        push @bind, '%'.$search->{'phone'}.'%';
    }
    if ($search->{'tviewer'} ne 'NOTSETYET') {
        push @clauses, 'tviewer LIKE ?';
        push @bind, '%'.$search->{'tviewer'}.'%';
    }
    if ($search->{'email'} ne 'NOTSETYET') {
        push @clauses, 'email LIKE ?';
        push @bind, '%'.$search->{'email'}.'%';
    }
    if (@clauses) {
        my $clause = join(' AND ', @clauses);
        $sql = "SELECT * FROM phonebook WHERE $clause ORDER BY name";
        $sth = $dbh->prepare($sql);
        $sth->execute(@bind);
        #$sth->execute( "Avebury", "%largest stone circle%" );
    }
    else {
        $sql = 'SELECT * FROM phonebook ORDER BY name';
        # $sql = 'SELECT * FROM phonebook ORDER BY company, name';
        $sth = $dbh->prepare($sql);
        $sth->execute();
    }
    my $numRows = $sth->rows;
    print pre("Could not find a contact within database.") unless $numRows;
    print pre( "Number of rows is: " . $numRows);
    while (my $row = $sth->fetchrow_hashref) {
        warn( Dumper($row) );
        my %contact = ();
        my $output = "id: $row->{'id'}\tcustomer: $row->{'customer'}\tname: $row->{'name'}";
        warn($output);
        $contact{'id'}          = $row->{'id'};
        $contact{'company'}          = $row->{'company'};
        $contact{'name'}          = $row->{'name'};
        $contact{'phone'}          = $row->{'phone'};
        $contact{'tviewer'}          = $row->{'tviewer'};
        $contact{'email'}          = $row->{'email'};
        $contact{'comment'}          = $row->{'comment'};
        push(@contacts, \%contact);
    } # END while
    $sth->finish();
    # Disconnect from the database.
    $dbh->disconnect();
    return @contacts;
}

#=============================
# sub back_to_main
#=============================
sub back_to_main {
    my $timeout = shift || 5;
    my $title = shift || 'New phonebook entry saved';
    my $name = shift || '';
    my $url = ( $name ? $script_name.'?s_name='.$name : $script_name );
    warn("url is: $url");

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
        <a href='$script_name'>Back to the main page</a>
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
