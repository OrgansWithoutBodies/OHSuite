<template>
<div class = "card">
<b class = "name"> {{donor.lastname}}, {{donor.firstname}}</b> <p/>
<i class = "address"> {{donor.address}}</i><p/>
<u class = "phone"> {{donor.phone}}</u>
</div>
</template>

<script>
export default {
  name: 'DonorCard',
  props: { donor: {
    type: Object,
    required: true
  }},
  data () {
    return {
      donor: donor
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
.card{
background-color:#dddddd;
border:2px solid #999999;
position:relative;
min-width: 100px;
max-width: 300px;
box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);
transition: 0.3s;
border-radius: 5px;
}
.phone {
color: #42b983;
}
.phone:before{
content:"";
display:inline;
width:10px;
height:10px;
color:#ff0000;
}
</style>
<!--@todo rolodex style name tab - loc based on lastname-->
