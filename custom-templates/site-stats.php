<?php
/*
Template Name: Site Stats
*/
?>

<title>Site Stats</title>
<p><a href="/">Home</a></p>

<?php
  $query_img_args = array(
    'post_type' => 'attachment',
    'post_mime_type' =>array(
                    'jpg|jpeg|jpe' => 'image/jpeg',
        ),
    'post_status' => 'inherit',
    'posts_per_page' => -1,
    );
  $query_img = new WP_Query( $query_img_args );
  echo 'Total jpegs: ' .$query_img->post_count. ' ';
?>
<br>

<?php
  $query_img_args = array(
    'post_type' => 'attachment',
    'post_mime_type' =>array(
                    'gif' => 'image/gif',
        ),
    'post_status' => 'inherit',
    'posts_per_page' => -1,
    );
  $query_img = new WP_Query( $query_img_args );
  echo 'Total gifs: ' .$query_img->post_count. ' ';
?>
<br>

<?php
  $query_img_args = array(
    'post_type' => 'attachment',
    'post_mime_type' =>array(
                    'mp4' => 'video/mp4',
        ),
    'post_status' => 'inherit',
    'posts_per_page' => -1,
    );
  $query_img = new WP_Query( $query_img_args );
  echo 'Total mp4\'s: ' .$query_img->post_count. ' ';
?>
<br>


<?php
// function courtesy of https://stackoverflow.com/a/2510459
function formatBytes($bytes, $precision = 2) {
    $units = array('B', 'KB', 'MB', 'GB', 'TB');

    $bytes = max($bytes, 0);
    $pow = floor(($bytes ? log($bytes) : 0) / log(1024));
    $pow = min($pow, count($units) - 1);

    // Uncomment one of the following alternatives
    // $bytes /= pow(1024, $pow);
     $bytes /= (1 << (10 * $pow));

    return round($bytes, $precision) . ' ' . $units[$pow];
}
?>

<?php
global $wpdb;

$wild = '%';
$fin = $wild . $wpdb->esc_like($srch) . $wild;
$result  = $wpdb->get_results( "SELECT * FROM  $wpdb->posts WHERE post_type = 'attachment' ORDER BY id desc");
$count = count($result);
$cur_dir = getcwd();
foreach ( $result as $posts ) {
   $result2 = $wpdb->get_results("SELECT * FROM $wpdb->postmeta WHERE post_id = '$posts->ID'");
    foreach ( $result2 as $metastuff ) {
      $attachment_data_array=unserialize($metastuff->meta_value);
      $file = $attachment_data_array['file'];
   }
   $file2 = '/mnt/storage1/websites/rnd/wp-content/uploads' . $file;
   // $file2 = $cur_dir . '/wp-content/uploads/' . $file;
   $fsize1 = filesize($file2);
//   $fsize = formatBytes($fsize1);
   $tsize += $fsize1;
}
$tsize2 = formatBytes($tsize);
echo "Total media files: $tsize2";
?>

