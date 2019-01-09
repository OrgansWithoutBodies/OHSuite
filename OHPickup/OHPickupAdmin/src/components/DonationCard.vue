<template>
<div class="card" draggable="true">
<b class="items"> </b> {{don.inputtime}}<p/>
<i class="address"></i><p/>
<u class="phone"> {{don.donor.phone}}</u>
<input type="button" class="hidebtn" value="Hide Donation">
<input type="button" class="delbtn" value="Delete Donation">
</div>
</template>

<script>
export default {
  name: 'DonorCard',
  data () {
    return {
      don: {inputtime: 1234,
        scheduleddate: 12345,
        status: 'Unmarked',
        items: 'None',
        donor: {firstname: 'Test',
          lastname: 'Testerson',
          address: '215 test ct',
          phone: '12345',
          email: 'test'}}
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
.hidebtn{
  background-color:#f2ed4e;
}
.delbtn{
  background-color:#ff0000;
}
</style>
