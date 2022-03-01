<body <?php body_class(); ?>>
<?php wp_body_open(); ?>

<div id="main">

<div id="header">
<a href="/blog"><img src="<?php echo get_template_directory_uri(); ?>/images/mclogo2.jpg" /></a>
<?php get_header(); ?>
</div>
<div id="sidebar"><?php get_sidebar(); ?></div>
<div id="content">

<?php if (have_posts()) : ?><?php while (have_posts()) : the_post(); ?>
<?php
if(has_tag()) {
$post_tags = get_the_tags();
if (strpos($post_tags[0]->name, 'tt') === 0) {
?>

<div class="post" style="background-color: #740000;padding: 4px;border-bottom: 1px solid rgb(0 0 0);">


<?php
$imdbid = $post_tags[0]->name;

$dir = 'sqlite:/home/coax/websites/hidden3/html/databases/movies-flm.db';
$dbh  = new PDO($dir, null, null, [PDO::SQLITE_ATTR_OPEN_FLAGS => PDO::SQLITE_OPEN_READONLY]) or die("cannot open the database");
$query = "select * from flmlist where imdb like '%" . $imdbid . "%' group by imdb order by year desc";
foreach ($dbh->query($query) as $row) {
?> <h1 style="display:inline;">Movie info:</h1> <h2 style="display:inline;"> <a style="color:white;" href="<?php the_permalink(); ?>"><?php echo $row[2]; ?></a> (<?php echo $row[8]; ?>) </h2> <?php
$im_final = $row[0] . '.jpg';
?>
<br><br>
    
<img style="display:inline;" src=https://hidden.machinecode.org/static/covers_flm/<?php echo $im_final; ?> width="200" />

<br><h2>Info:</h2><br>
<div class="infos"> Title: <?php echo $row[2]; ?> </div>
<div class="infos"> English Title: <?php echo $row[1]; ?> </div>
<div class="infos"> Director: <?php echo $row[3]; ?> </div>
<div class="infos"> Stars: <?php echo $row[4]; ?> </div>
<div class="infos"> Genres: <?php echo $row[5]; ?> </div>
<div class="infos"> Plot: <?php echo $row[7]; ?> </div>
<div class="infos"> Country: <?php echo $row[9]; ?> </div>
<div class="infos"> Language: <?php echo $row[10]; ?> </div>
<div class="infos"> IMDB: <?php echo $row[0]; ?> </div>
    <br><h2>Gallery:</h2><br>
<?php
$img_dir = '/home/coax/websites/hidden3/html/static/flm_images/' . $row[0];
if (file_exists($img_dir)) {
    $files = glob("$img_dir/*");
    sort($files, SORT_NATURAL | SORT_FLAG_CASE);
    foreach ($files as $file) {
    $file_final = explode("/", $file); ?>
  <a href="https://hidden.machinecode.org/static/flm_images/<?php echo $file_final[8]; ?>/<?php echo $file_final[9]; ?>"><img src="https://hidden.machinecode.org/static/flm_images/<?php echo $file_final[8]; ?>/<?php echo $file_final[9]; ?>" width="90" /></a> 


    
<?php }} ?>
    

    <br><br><h2>The review:</h2>
    <?php the_content('-> read more'); ?>
    </div>
<br><br>
    
<?php                                    
}}
$dbh = null;
} else { ?>
    <div class="title"><h2><a href="<?php the_permalink(); ?>"><?php the_title(); ?></a></h2><div class="subhead"><?php the_time('F jS, Y') ?></div></div>
    <div class="post">
    <?php the_content('-> read more'); ?>
    </div>
<?php
}
?>

<?php endwhile; ?>
<?php endif; ?>
<?php next_posts_link(__('&laquo; Previous Entries', 'code2center')) ?><br>
<?php previous_posts_link(__('Newer Entries &raquo;','code2center')); ?>
</div>
</div>
</body>