<?php
/*
Template Name: FLM SQLite3
apt-get install php-sqlite3
*/
?>
<?php get_header(); ?>

<style type="text/css">
td {
padding: 15px;
border: 1px solid #316291;
}
</style>


<h2 style="text-align: center;"><?php the_title() ; ?></h2>

<?php the_content('more))'); ?>
<br><br>

<table style="border-collapse: collapse;">
<tbody>


<?php

$dir = 'sqlite:/home/coax/websites/rnd/wp-content/movies-flm.db';
$dbh  = new PDO($dir, null, null, [PDO::SQLITE_ATTR_OPEN_FLAGS => PDO::SQLITE_OPEN_READONLY]) or die("cannot open the database");
//$query =  "SELECT * FROM moviesflm order by year desc";
$query = "select moviesflm.*, actressflm.actress, flm_actress2.name, flm_actress2.actress_born from moviesflm left join actressflm on substr(moviesflm.title, -7, -100) = actressflm.title collate nocase left join flm_actress2 on flm_actress2.films like '%' || moviesflm.imdb || '%' group by moviesflm.imdb order by year desc";
	
foreach ($dbh->query($query) as $row)
{
$img_file =  explode('/', $row[0]);
$im_final = $img_file[4] . '.jpg';
?>
<tr>
<td class="cover"><img src=/wp-content/covers/<?php echo $im_final; ?> width="200" /><br>
</td>
<td class="infobox">
<h2><?php echo $row[1]; ?></h2>
<br>

<div class="titl3" style="width: 320px;"></div>
<b>Genre:</b> <?php echo $row[4]; ?><br>
<b>Plot:</b> <?php echo $row[6]; ?><br>
<b>Director:</b> <?php echo $row[2]; ?><br>
<b>Main stars:</b> <?php echo $row[5]; ?><br>
<b>Country:</b> <?php echo $row[8]; ?><br>
<b>Language:</b> <?php echo $row[9]; ?><br>
<b>IMDB:</b> <?php echo $row[0]; ?><br>
</td>
<td class="child_Stars">
<div class="titl" style="width: 180px;"></div><br>

<?php
$child_stars = explode(', ', $row[12]);
$img_dir3 = '/home/coax/websites/rnd/wp-content/flm_actress/' . str_replace(' ', '_', $child_stars[0]) . '.jpg';
foreach ($child_stars as $child_star) {
$child_star_image = str_replace(' ', '_', $child_star);
if (file_exists($img_dir3)) {
?>
<img src="/wp-content/flm_actress/<?php echo $child_star_image; ?>.jpg" /><br>

<?php
}
?> <?php echo $child_star;  ?> <br><br> <?php
}
?>
</td>


<td>

<?php

$img_dir = '/home/coax/websites/rnd/wp-content/flm_images/' . $img_file[4];
if (file_exists($img_dir)) {
    $files = glob("$img_dir/*");
    sort($files, SORT_NATURAL | SORT_FLAG_CASE);
    //echo var_dump($files);
    foreach ($files as $file) {
    $file_final = explode("/", $file); ?>
  <a href="/wp-content/flm_images/<?php echo $file_final[7]; ?>/<?php echo $file_final[8]; ?>"><img src="/wp-content/flm_images/<?php echo $file_final[7]; ?>/<?php echo $file_final[8]; ?>" width="90" /></a>
<?php
}
    //var_dump($files);
    //echo "The directory $img_dir exists";
} else {
    echo '<div class="tabl" style="width: 400px;"> No gallery yet </div>';
}
?>

</td>
</tr>
<?php
}
$dbh = null;
?>
</tbody>
</table>

<?php get_footer(); ?>

