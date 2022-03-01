<?php
/*
Template Name: Videos Single Page
*/
?>

        <?php
if ( $post->post_parent ) {
    $children = wp_list_pages( array(
        'title_li' => '',
        'child_of' => $post->post_parent,
        'echo'     => 0
    ) );
   $page_link = get_page_link( $post->post_parent );
    $title = get_the_title( $post->post_parent );
} else {
    $children = wp_list_pages( array(
        'title_li' => '',
        'child_of' => $post->ID,
        'echo'     => 0
    ) );
    $page_link = get_page_link( $post->post_parent );
    $title = get_the_title( $post->ID );
}

if ( $children ) : ?>
    <h2><?php echo '<center>Part of gallery: <a href=' . $page_link .'>' . $title . '</a></center>'; ?></h2>
<?php endif; ?>



<?php
$args = array('post_type'=>'attachment','numberposts'=>-1,'post_status'=>null, 'post_mime_type'=>'video', 'orderby' => 'CAST(substring(title, -2) as unsigned integer)', 'order' => 'ASC', 'post_parent'=>$post->ID);

echo "<title>$post->post_title</title>";

echo "<h1>$post->post_title</h1>";

   $attachments = get_posts($args);
    if($attachments){
          foreach($attachments as $attachment){
           echo "<h2>$attachment->post_title<h2>";
           echo "<p><video controls> <source src='$attachment->guid' type='video/mp4'>Your browser does not support the video tag.</video></p>";
           }
      }

?>
