<?php
/*
Template Name: Attachments Paginated Search
*/
?>

<style type="text/css">
table, th, td {
border: 1px solid black;
border-collapse: collapse;
}
.pagination {
font-size: 25px;
text-align: center;
width: 100%;
display: inline-block;
margin-left: auto;
margin-right: auto;
font-size: 35px;
letter-spacing: 5px;
margin-bottom: 25px;
}
</style>

<form method='post' action='?'>
<div><input type='text' name='fname' placeholder='File name'>
<input type='submit'>
</div>
</form>


<?php
if(isset($_GET['fname'])) {
    $srch = $_GET['fname'];
} else {
    $srch = $_POST['fname'];
}
?>

<?php
echo "search term: $srch ";
?>

<br>
<a href="<?php echo get_permalink(); ?>">reset search</a>


<?php
if(isset($_POST['fname'])) {
$redir = add_query_arg( 'fname', $srch );
wp_safe_redirect($redir); 
exit();
}
?>



<title><?php echo esc_html(get_the_title()); ?></title>

<h2><a href="/">Home</a> -> <?php the_title(''); ?></h2>

<?php the_content(); ?>

<?php
$paged = ( get_query_var( 'paged' ) ) ? absint( get_query_var( 'paged' ) ) : 1;

$wp_query = new WP_Query(array(
'post_type' => 'attachment',
'post_status' => 'any',
'post_mime_type' => 'image',
'orderby' => array('modified' => 'desc'),
'paged' => $paged,
's' => $srch
));
?>
<?php $count = $wp_query->found_posts; echo 'Number of images: ' . $count ?>
<div class="gallerytiles">

<table style="width:100%">
<?php if ( $wp_query->have_posts() ) : ?>

<?php while ( $wp_query->have_posts() ) : $wp_query->the_post(); ?>

<?php
$metadata = wp_get_attachment_metadata(get_the_ID());
$uploads = wp_upload_dir();
$baseurl2 = $uploads['path'];
$width = $metadata['width'];
$height = $metadata['height'];
$caption = $metadata['image_meta']['caption'];
$camera = $metadata['image_meta']['camera'];
$copyright = $metadata['image_meta']['copyright'];
$aperture = $metadata['image_meta']['aperture'];
$timestamp = $metadata['image_meta']['created_timestamp'];
$credit = $metadata['image_meta']['credit'];
$title = $metadata['image_meta']['title'];
$focal_length = $metadata['image_meta']['focal_length'];
$iso = $metadata['image_meta']['iso'];
$shutter_speed = $metadata['image_meta']['shutter_speed'];
$orientation = $metadata['image_meta']['orientation'];
$keywords1 = $metadata['image_meta']['keywords'][0];
$keywords2 = $metadata['image_meta']['keywords'];
$uploaded = esc_attr(get_the_time());
$date3 = get_the_date();
$url3 = esc_url(wp_get_attachment_url());
$post_url = esc_url(get_permalink($wp_query->post_parent));
$post_title = get_the_title($post->post_parent);
$file = $baseurl2 . $metadata['file'];
$mimetype = get_post_mime_type();
?>

<tr>

<th><a href="<?php echo $url3; ?>"><?php echo wp_get_attachment_image( get_the_ID(), array('700', '600'), "", 'medium' );  ?></a></th>

<th>

Title: <?php the_title(); ?><br>
Link: <a href="<?php echo get_permalink(); ?>"><?php echo get_permalink(); ?></a><br>
Uploaded: <?php echo $date3; ?> <?php echo $uploaded; ?> <br>
File Url: <a href="<?php echo $url3; ?>"><?php echo $url3; ?></a><br>
Mime type: <?php echo $mimetype; ?> <br><br>

<h2>Metadata:</h2>
Width: <?php echo $width; ?> <br>
Height: <?php echo $height; ?> <br>
Camera: <?php echo $camera; ?> <br>
Date taken: <?php echo gmdate("Y-m-d H:i:s", $timestamp); ?> <br>
Caption: <?php echo $caption; ?> <br>
Copyright: <?php echo $copyright; ?> <br>
Credit: <?php echo $credit; ?> <br>
Title: <?php echo $title; ?> <br>
Aperture: <?php echo $aperture; ?> <br>
Focal length: <?php echo $focal_length; ?> <br>
ISO: <?php echo $iso; ?> <br>
Shutter speed: <?php echo $shutter_speed; ?> <br>
Orientation: <?php echo $orientation; ?> <br>
Keywords: <br> <?php foreach ($keywords2 as $value){echo $value . '<br>';} ?>

</th>

<?php endwhile; ?>
</tr>
</table>
       </div>
        <div class="pagination">

<?php
echo paginate_links( array(
    'prev_next'    => true,
    'prev_text'    => sprintf( '<i></i> %1$s', __( '<-', 'text-domain' ) ),
    'next_text'    => sprintf( '%1$s <i></i>', __( '->', 'text-domain' ) ),
) );
?>
</div>

<?php wp_reset_postdata(); ?>

<?php else : ?>
    <p><?php _e( 'Sorry, no posts matched your criteria.' ); ?></p>
<?php endif; ?>

