<template>
<Message :messages="messages" />
</template>

<script>
import Message from "@/components/widgets/message.vue";
import avatar2 from '@/assets/images/users/avatar-2.jpg'
import avatar3 from '@/assets/images/users/avatar-3.jpg'
import avatar4 from '@/assets/images/users/avatar-4.jpg'
import avatar5 from '@/assets/images/users/avatar-5.jpg'
import avatar6 from '@/assets/images/users/avatar-6.jpg'
export default {
    components: { Message },
    data() {
        return {
            messages: [{
                    image: avatar2,
                    name: 'Tomaslau',
                    message: "I've finished it! See you so...",
                },
                {
                    image: avatar3,
                    name: 'Stillnotdavid',
                    message: 'This theme is awesome!',
                },
                {
                    image: avatar4,
                    name: 'Kurafire',
                    message: 'Nice to meet you',
                },
                {
                    image: avatar5,
                    name: 'Shahedk',
                    message: "Hey! there I'm available...",
                },
                {
                    image: avatar6, 
                    name: 'Adhamdannaway',
                    message: 'This theme is awesome!',
                },
            ],
        }
    },
}
</script>
