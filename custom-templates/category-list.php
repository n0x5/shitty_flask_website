<?php
/*
Template Name: Category list
*/
?>
<title>site index</title>

<p><a href="/">Home</a></p>



<?php
global $wpdb;

$result  = $wpdb->get_results( "SELECT * FROM  $wpdb->terms ORDER BY name asc");
$count = count($result);
echo "Categories found: $count <br><br>";
foreach ( $result as $category ) {
    echo "$category->name <br>\n";
    $result_posts  = $wpdb->get_results( "SELECT * FROM  $wpdb->term_relationships WHERE term_taxonomy_id = '$category->term_id' ORDER BY object_id desc");
    $count = count($result);
         foreach ( $result_posts as $post ) {
           $post_title3 = $wpdb->get_results( "SELECT * FROM  $wpdb->posts WHERE ID = '$post->object_id' ORDER BY ID asc");
           foreach ( $post_title3 as $title3 ) { ?>
<?php echo $title3->post_date; ?>&nbsp&nbsp <?php echo $title3->post_title; ?> &nbsp&nbsp <a href="<?php echo $title3->guid; ?>"><?php echo $title3->guid; ?></a><br>
             
<?php
}
}

}
?>

<br><br><br>
<?php
global $wpdb;

$result  = $wpdb->get_results( "SELECT * FROM  $wpdb->posts WHERE post_type = 'page' ORDER BY post_name asc");
$count = count($result);
echo "Pages found: $count <br><br>";
foreach ( $result as $category ) { ?>
	<?php echo $category->post_date; ?>&nbsp&nbsp <?php echo $category->post_title; ?> &nbsp&nbsp <a href="<?php echo $category->guid; ?>"><?php echo $category->guid; ?></a><br>
<?php    

}


?>