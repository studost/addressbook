<?php
// https://www.html.de/threads/php-mysql-kleines-telefonbuch-mit-php-und-mysql.13402/
// 2018_05_16, studo
//
error_reporting(E_ALL);
include("inc/connect.php");
$meldung = "";
$auswahl = "id";

if(isset($_POST['eintragen'])){
  
  if(empty($_POST['name']) || empty($_POST['phone'])){
 
  $meldung = "Bitte geben Sie die notwendigen Kontaktdaten ein!";
  
  }
  else{
  
      $name = $_POST['name'];
      $company = $_POST['company'];
      $phone = $_POST['phone'];
      $tviewer = $_POST['tviewer'];
      $comment = $_POST['comment'];
      $email = $_POST['email'];
  
  $eintragen = mysql_query("INSERT INTO phonebook SET 
                                 name = '".$name."', 
                                 company = '".$company."', 
                                 phone = '".$phone."',
                                 email = '".$email."'
                                 ");
}
}

    if(isset($_GET['aktion'])){
     $job = mysql_query("DELETE FROM phonebook WHERE id = '".$_GET['objekt']."' ");
      }
      
    if(isset($_GET['auswahl'])){
      $auswahl = $_GET['auswahl'];
      }
  
?>

<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
<title>Telefonbuch</title>
<meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1">
</head>
<body>

<?php

$anzeigen = mysql_query("SELECT * FROM phonebook ORDER BY ".$auswahl."");

echo "<table id='tabelle_ausgabe' border='1'>";
echo "<tr>";
echo "<th>Name</th><th>company</th><th>phone</th><th>Email</th>";
echo "<th>entfernen</th>";
echo "<th>";
echo "<form method='get' action='".$_SERVER['PHP_SELF']."'>";
echo "<select name='auswahl'>";
echo "<option value='id'>sortieren nach:</option>";
echo "<option value='name'>Name</option>";
echo "<option value='company'>company</option>";
echo "<option value='phone'>phone</option>";
echo "<option value='email'>Email</option>";
echo "</select>"; 
echo "</th>";
echo "<th>";
echo "<input type='submit' name='sortieren' value='OK'/>";
echo "</th>";
echo "</form>";
echo "</tr>";

while($ausgabe = mysql_fetch_array($anzeigen)){
    echo "<tr>";
    echo "<td>".$ausgabe['name']."</td>";
    echo "<td>".$ausgabe['company']."</td>";
    echo "<td>".$ausgabe['phone']."</td>";
    echo "<td>".$ausgabe['email']."</td>";
    echo "<td><a href='".$_SERVER['PHP_SELF']."?aktion=delete&objekt=".$ausgabe['id']."'>entfernen</a></td><td>&nbsp;</td><td>&nbsp;</td>";
    echo "</tr>";
}

echo "</table>";

?>

<h4>Neuen Kontakt hinzufügen:</h4>
<p><? echo $meldung; ?></p>
<table border="1">
<form name="form" action="<? $_SERVER['PHP_SELF'] ?>" method="post">
<tr>
<td><label for="name">Name:</label></td>
<td><input type="text" name="name"></td>
</tr>
<tr>
<td><label for="company">company:</label></td>
<td><input type="text" name="company"></td>
</tr>
<tr> 
<td><label for="phone">Telefon:</label></td>
<td><input type="text" name="phone"></td>
</tr>
<tr> 
<td><label for="email">Email:</label></td>
<td><input type="text" name="email"></td>
</tr>
<tr> 
<td><label for="senden">&nbsp;</label></td>
<td><input type="submit" name="eintragen" value="Eintragen"></td>
</tr> 
</form>
</table>

</body>
</html>



