import avatar1 from '@/assets/images/users/avatar-1.jpg'
import avatar2 from '@/assets/images/users/avatar-2.jpg'
import avatar4 from '@/assets/images/users/avatar-4.jpg'
import avatar5 from '@/assets/images/users/avatar-5.jpg'
import avatar6 from '@/assets/images/users/avatar-6.jpg'
import avatar8 from '@/assets/images/users/avatar-8.jpg'
import avatar9 from '@/assets/images/users/avatar-9.jpg'
import avatar10 from '@/assets/images/users/avatar-10.jpg'

const todoData = [
    {
        id: 1,
        priority: 'High',
        title: 'iOS App home page',
        date: '18 Jul 2018',
        project: 'iOS',
        comments: 74,
        image: avatar2,
        assign: 'Robert Carlile'
    },
    {
        id: 2,
        priority: 'Medium',
        title: 'Topnav layout design',
        date: '18 Jul 2018',
        project: 'Hyper',
        comments: 28,
        image: avatar1,
        assign: 'Coder Themes'
    },
    {
        id: 3,
        priority: 'Low',
        title: 'Invite user to a project',
        date: '11 Jul 2018',
        project: 'CRM',
        comments: 68,
        image: avatar2,
        assign: 'Lucas Hardy'
    },
];

const progressData = [
    {
        id: 4,
        priority: 'Medium',
        title: 'Write a release note',
        date: '22 Jun 2018',
        project: 'Hyper',
        comments: 17,
        image: avatar5,
        assign: 'Sean White'
    },
    {
        id: 5,
        priority: 'Low',
        title: 'Enable analytics tracking',
        date: '19 Jun 2018',
        project: 'CRM',
        comments: 48,
        image: avatar6,
        assign: 'Louis Allen'
    },
];

const reviewData = [
    {
        id: 6,
        priority: 'High',
        title: 'Kanban board design',
        date: '2 May 2018',
        project: 'CRM',
        comments: 65,
        image: avatar1,
        assign: 'Coder Themes'
    },
    {
        id: 7,
        priority: 'Medium',
        title: 'Code HTML email template',
        date: '7 May 2018',
        project: 'CRM',
        comments: 106,
        image: avatar9,
        assign: 'Zak Turnbull'
    },
    {
        id: 8,
        priority: 'Medium',
        title: 'Brand logo design',
        date: '8 Jul 2018',
        project: 'Design',
        comments: 68,
        image: avatar8,
        assign: 'Lily Parkin'
    },
    {
        id: 9,
        priority: 'High',
        title: 'Kanban board design',
        date: '22 Jul 2018',
        project: 'CRM',
        comments: 39,
        image: avatar4,
        assign: 'Riley Steele'
    },
];

const doneData = [
    {
        id: 10,
        priority: 'Low',
        title: 'Dashboard design',
        date: '16 Jul 2018',
        project: 'Hyper',
        comments: 287,
        image: avatar10,
        assign: 'Harvey Dickinson'
    }
];

export {todoData, progressData, reviewData, doneData};
