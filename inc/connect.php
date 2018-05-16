<?php
// connect.php
// 2018_05_16
// studo
$host = "Servername";
$user = "Benutzer";
$pass = "Passwort";
$db = "DatenbankName";

$verbinden = @mysql_connect($host,$user,$pass) OR die(mysql_error());
//$verbinden = mysql_connect($host,$user,$pass);
//if(!$verbinden){echo "Server konnte nicht gefunden werden!";}

$set_db = mysql_select_db($db) OR die (mysql_error());
//if(!$set_db){echo "Datenbank konnte nicht gefunden werden!";}


