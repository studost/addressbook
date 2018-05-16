<?php
// https://www.html.de/threads/php-mysql-kleines-telefonbuch-mit-php-und-mysql.13402/
// 2018_05_16, studo
//
error_reporting(E_ALL);
include("inc/connect.php");
$meldung = "";
$auswahl = "id";

if(isset($_POST['eintragen'])){
  
  if(empty($_POST['name']) || empty($_POST['telefon'])){
 
  $meldung = "Bitte geben Sie die notwendigen Kontaktdaten ein!";
  
  }
  else{
  
      $name = $_POST['name'];
      $vorname = $_POST['vorname'];
      $telefon = $_POST['telefon'];
      $email = $_POST['email'];
  
  $eintragen = mysql_query("INSERT INTO telefonbuch SET 
                                 name = '".$name."', 
                                 vorname = '".$vorname."', 
                                 telefon = '".$telefon."',
                                 email = '".$email."'
                                 ");
}
}

    if(isset($_GET['aktion'])){
     $job = mysql_query("DELETE FROM telefonbuch WHERE id = '".$_GET['objekt']."' ");
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

$anzeigen = mysql_query("SELECT * FROM telefonbuch ORDER BY ".$auswahl."");

echo "<table id='tabelle_ausgabe' border='1'>";
echo "<tr>";
echo "<th>Name</th><th>Vorname</th><th>Telefon</th><th>Email</th>";
echo "<th>entfernen</th>";
echo "<th>";
echo "<form method='get' action='".$_SERVER['PHP_SELF']."'>";
echo "<select name='auswahl'>";
echo "<option value='id'>sortieren nach:</option>";
echo "<option value='name'>Name</option>";
echo "<option value='vorname'>Vorname</option>";
echo "<option value='telefon'>Telefon</option>";
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
    echo "<td>".$ausgabe['vorname']."</td>";
    echo "<td>".$ausgabe['telefon']."</td>";
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
<td><label for="vorname">Vorname:</label></td>
<td><input type="text" name="vorname"></td>
</tr>
<tr> 
<td><label for="telefon">Telefon:</label></td>
<td><input type="text" name="telefon"></td>
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



